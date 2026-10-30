from collections import defaultdict, OrderedDict
from functools import wraps
from mimetypes import guess_type
from os import path
from urllib.parse import quote, urlparse
from io import BytesIO

import exifread
import hmac
import json
import time
from sh import convert, TimeoutException
from thumbnail_gate import ThumbnailGate
from threading import BoundedSemaphore
from metadata_reader import read_metadata, MetadataError
from botocore.exceptions import ClientError

import settings
from bottle import (
    Response, request, response, static_file, template, abort,
    HTTPResponse, route, redirect
)


from bottle import error
from app_logging import configure_logging, logger, RequestLogging, abort_with_reason
configure_logging(settings.LOG_LEVEL)

@error(500)
def show_500(exc):
    exception = getattr(exc, 'exception', None)
    logger.error('request_error', exc_info=(type(exception), exception, exception.__traceback__)
                 if exception else None)
    return 'Internal Server Error'


# S3 client (shared)
from storage import create_storage
s3, storage_backend = create_storage(settings)
thumbnail_slots = ThumbnailGate(getattr(settings, 'THUMBNAIL_CONCURRENCY', 1),
                                getattr(settings, 'THUMBNAIL_QUEUE_SIZE', 5))

metadata_slots = BoundedSemaphore(getattr(settings, 'METADATA_CONCURRENCY', 1))

logger.info('storage_initialized', extra={'fields': {'backend': storage_backend}})

### Token/Auth helpers (unchanged semantics) ###
def generate_token(timestamp, filename):
    """Generate the auth token for the given filename and timestamp.
    This is for comparing to the client submited token.
    """
    timestamp = str(timestamp)
    mac = hmac.new(settings.KEY.encode(), timestamp.encode() + filename.encode(), 'md5')
    return ':'.join((mac.hexdigest(), timestamp))


class TokenException(Exception):
    """Raised when an auth token is invalid for some reason."""
    def __init__(self, message, reason='invalid_token'):
        super().__init__(message)
        self.reason = reason


def get_timestamp():
    """Return an integer timestamp with one second resolution for
    the current moment.
    """
    return int(time.time())


def validate_token(token_in, filename):
    """Validate the input token for given filename using the secret key
    in settings. Checks that the token is within the time tolerance and
    is valid.
    """
    if settings.KEY is None:
        return
    if not token_in or ':' not in token_in:
        raise TokenException("Auth token is missing or malformed.",
                             "missing_token" if not token_in else "malformed_token")
    mac_in, timestr = token_in.split(':', 1)
    try:
        timestamp = int(timestr)
    except ValueError:
        raise TokenException("Auth token is malformed.", "malformed_token")
    if settings.TIME_TOLERANCE is not None:
        current_time = get_timestamp()
        if not abs(current_time - timestamp) < settings.TIME_TOLERANCE:
            raise TokenException(
                "Auth token timestamp out of range: %s vs %s" % (timestamp, current_time), "expired_token"
            )
    if token_in != generate_token(timestamp, filename):
        raise TokenException("Auth token is invalid.")


def require_token(filename_param, always=False):
    """Decorate a view function to require an auth token to be present for access.

    filename_param defines the field in the request that contains the filename
    against which the token should validate.

    If REQUIRE_KEY_FOR_GET is False, validation will be skipped for GET and HEAD
    requests.

    Automatically adds the X-Timestamp header to responses to help clients stay
    syncronized.
    """

    def decorator(func):
        @include_timestamp
        @wraps(func)
        def wrapper(*args, **kwargs):
            if always or request.method not in ('GET', 'HEAD') or settings.REQUIRE_KEY_FOR_GET:
                params = request.forms if request.method == 'POST' else request.query
                try:
                    validate_token(params.token, params.get(filename_param))
                except TokenException as e:
                    request.environ['asset.error_reason'] = e.reason
                    response.content_type = 'text/plain; charset=utf-8'
                    response.status = 403
                    return str(e)
            return func(*args, **kwargs)
        return wrapper
    return decorator


def include_timestamp(func):
    """Decorate a view function to include the X-Timestamp header to help clients
    maintain time syncronization.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except HTTPResponse as result:
            result.set_header('X-Timestamp', str(get_timestamp()))
            raise
        target = result if isinstance(result, Response) else response
        target.set_header('X-Timestamp', str(get_timestamp()))
        return result
    return wrapper


def allow_cross_origin(func):
    """Decorate a view function to allow cross domain access."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except HTTPResponse as r:
            r.set_header('Access-Control-Allow-Origin', '*')
            raise
        target = result if isinstance(result, Response) else response
        target.set_header('Access-Control-Allow-Origin', '*')
        return result
    return wrapper


### S3 URI / key helpers ###
def parse_s3_uri(s3_uri):
    """
    Parse s3://bucket/prefix and return (bucket, prefix_without_trailing_slash)
    """
    parsed = urlparse(s3_uri)
    if parsed.scheme != 's3' or not parsed.netloc:
        raise ValueError(f"Invalid S3 URI: {s3_uri!r}")
    return parsed.netloc, parsed.path.lstrip('/').rstrip('/')

def get_collection_base(coll):
    """
    Return (bucket, base_prefix) for the collection, or 404 if unknown.
    """
    if storage_backend == 'local':
        directories = getattr(settings, 'COLLECTION_DIRS', None)
        if directories is None:
            return settings.BASE_DIR, ''
        if coll not in directories:
            abort_with_reason(404, 'unknown_collection', 'Unknown collection')
        return path.join(settings.BASE_DIR, directories[coll]), ''
    try:
        s3_uri = settings.COLLECTION_S3_PATHS[coll]
    except KeyError:
        abort_with_reason(404, 'unknown_collection', 'Unknown collection')
    try:
        return parse_s3_uri(s3_uri)
    except ValueError as e:
        abort_with_reason(500, 'invalid_storage_configuration', 'Invalid storage configuration')


def make_s3_key(coll, thumb, filename=''):
    """
    Build bucket and key for given collection, thumb/orig, and filename.
    """
    if filename and (filename in ('.', '..') or '/' in filename or '\\' in filename or '\x00' in filename):
        abort_with_reason(400, 'invalid_filename', 'Attachment filename must be a single filename')
    bucket, base_prefix = get_collection_base(coll)
    subdir = settings.THUMB_DIR if thumb else settings.ORIG_DIR
    parts = []
    if base_prefix:
        parts.append(base_prefix)
    parts.append(subdir)
    if filename:
        parts.append(filename)
    key = '/'.join(p.strip('/') for p in parts)
    return bucket, key


def stream_s3_object(bucket, key):
    """Retrieve object from S3, abort 404 if missing."""
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
    except ClientError as e:
        if e.response['Error']['Code'] in ('404', 'NoSuchKey'):
            abort_with_reason(404, 'asset_not_found', 'Attachment not found')
        raise
    try:
        return obj['Body'].read(), obj.get('ContentType', 'application/octet-stream')
    finally:
        obj['Body'].close()


def public_origin():
    protocol = request.headers.get('X-Forwarded-Proto', request.urlparts.scheme)
    host = settings.SERVER_NAME
    # Explicit ports in SERVER_NAME remain supported, including IPv6 literals.
    parsed = urlparse('//' + host)
    if parsed.port is None and settings.SERVER_PORT != (443 if protocol == 'https' else 80):
        host += ':' + str(settings.SERVER_PORT)
    return f'{protocol}://{host}'


def serve_object(bucket, key):
    if storage_backend == 'local':
        target = s3._path(bucket, key)
        return static_file(target.name, root=str(target.parent))
    from s3_http import serve_s3
    return serve_s3(s3, bucket, key)


def resolve_s3_key():
    """
    Determine bucket+key for requested file or thumbnail. Generate thumbnail if needed.
    Returns (bucket, key).
    """
    thumb_p = (request.query.get('type') == "T")
    coll = request.query.coll
    name = request.query.filename

    if not thumb_p:
        return make_s3_key(coll, False, name)

    # Thumbnail logic
    try:
        scale = int(request.query.scale)
    except (TypeError, ValueError):
        abort_with_reason(400, 'invalid_thumbnail_scale', 'Thumbnail scale must be an integer')
    if not 1 <= scale <= 4096:
        abort_with_reason(400, 'invalid_thumbnail_scale', 'Thumbnail scale must be between 1 and 4096')
    root, ext = path.splitext(name)
    # ImageMagick reads HEIC/HEIF; generate PNG thumbnails for these formats.
    if ext.lower() in ('.pdf', '.tiff', '.tif', '.heic', '.heif'):
        ext = '.png'
    thumb_name = f"{root}_{scale}{ext}"
    bucket, thumb_key = make_s3_key(coll, True, thumb_name)

    # If thumbnail exists, return it
    try:
        s3.head_object(Bucket=bucket, Key=thumb_key)
        logger.debug('thumbnail_cache_hit')
        return bucket, thumb_key
    except ClientError as e:
        if e.response['Error']['Code'] not in ('404', 'NoSuchKey'):
            raise

    if not thumbnail_slots.acquire(timeout=getattr(settings, 'THUMBNAIL_QUEUE_WAIT_SECONDS', 20)):
        abort_with_reason(503, 'thumbnail_busy', 'Thumbnail generation busy; retry later',
                          **{'Retry-After': '5'})
    try:
        # Another request may have generated this thumbnail while we waited.
        try:
            s3.head_object(Bucket=bucket, Key=thumb_key)
            return bucket, thumb_key
        except ClientError as e:
            if e.response['Error']['Code'] not in ('404', 'NoSuchKey'):
                raise
        # Need to generate thumbnail: fetch original
        orig_bucket, orig_key = make_s3_key(coll, False, name)
        try:
            obj = s3.get_object(Bucket=orig_bucket, Key=orig_key)
        except ClientError as e:
            if e.response['Error']['Code'] in ('404', 'NoSuchKey'):
                abort_with_reason(404, 'original_not_found', 'Original attachment not found')
            raise
        # Write temp files for ImageMagick processing
        from tempfile import TemporaryDirectory
        from contextlib import closing
        import shutil
        with closing(obj['Body']) as body, TemporaryDirectory(prefix='asset-thumbnail-') as tmp:
            local_orig = path.join(tmp, 'original' + path.splitext(name)[1])
            local_thumb = path.join(tmp, 'thumbnail' + ext)
            with open(local_orig, 'wb') as f:
                shutil.copyfileobj(body, f, length=64 * 1024)
            convert_args = ['-resize', f"{scale}x{scale}>"]
            if path.splitext(name)[1].lower() == '.pdf':
                convert_args += ['-background', 'white', '-flatten']
            # PR #35: select the first TIFF layer so ImageMagick writes one output
            # rather than numbered -0/-1 files. This also covers PDFs and sequences.
            local_orig += '[0]'
            try:
                limits = ['-limit', 'thread', '1',
                          '-limit', 'memory', getattr(settings, 'THUMBNAIL_MEMORY_LIMIT', '64MiB'),
                          '-limit', 'map', getattr(settings, 'THUMBNAIL_MAP_LIMIT', '64MiB'),
                          '-limit', 'disk', getattr(settings, 'THUMBNAIL_DISK_LIMIT', '512MiB')]
                convert(*limits, local_orig, *convert_args, local_thumb,
                        _timeout=getattr(settings, 'THUMBNAIL_TIMEOUT_SECONDS', 60))
            except TimeoutException:
                abort_with_reason(504, 'thumbnail_timeout', 'Thumbnail generation timed out')
            ctype, _ = guess_type(local_thumb)
            with open(local_thumb, 'rb') as f:
                s3.put_object(Bucket=bucket, Key=thumb_key, Body=f,
                              ContentType=ctype or 'application/octet-stream')

    finally:
        thumbnail_slots.release()

    logger.info('thumbnail_generated', extra={'fields': {'backend': storage_backend, 'scale': scale}})

    return bucket, thumb_key


### Routes ###
@route('/static/<path:path>')
def static_handler(path):
    """Serve local static files (unchanged)."""
    if not settings.ALLOW_STATIC_FILE_ACCESS:
        abort(404)
    if storage_backend == 'local':
        # Preserve master URLs relative to BASE_DIR.
        try:
            target = s3._path(settings.BASE_DIR, path)
        except ValueError:
            abort_with_reason(404, 'invalid_static_path', 'Attachment not found')
        return static_file(target.name, root=str(target.parent))

    parts = path.split('/', 1)
    if len(parts) != 2:
        abort(404, f"Bad static path: {path!r}")

    coll, rest = parts
    try:
        bucket, base_prefix = get_collection_base(coll)
    except KeyError:
        abort_with_reason(404, 'unknown_collection', 'Unknown collection')

    key = '/'.join(p for p in (base_prefix, rest) if p)
    return serve_object(bucket, key)


@route('/getfileref')
@allow_cross_origin
def getfileref():
    """Return the fileget URL for the requested attachment (client will append token etc)."""
    if not settings.ALLOW_STATIC_FILE_ACCESS:
        abort(404)

    coll = request.query.coll
    filename = request.query.filename

    # URL-encode the “collection/filename” into a single static path
    bucket, key = resolve_s3_key()
    _, prefix = get_collection_base(coll)
    relative = key[len(prefix.strip('/') + '/'):] if prefix else key
    if storage_backend == 'local':
        import os
        relative = os.path.relpath(s3._path(bucket, key), path.realpath(settings.BASE_DIR))
        static_path = quote(relative)
    else:
        static_path = f"{quote(coll, safe='')}/{quote(relative)}"
    url = f"{public_origin()}/static/{static_path}"

    response.content_type = 'text/plain; charset=utf-8'
    return url


@route('/fileget')
@require_token('filename')
def fileget():
    bucket, key = resolve_s3_key()
    result = serve_object(bucket, key)

    download_name = request.query.get('downloadname')
    if download_name:
        dl = quote(path.basename(download_name).encode('ascii', 'replace'))
        target = result if isinstance(result, HTTPResponse) else response
        target.set_header(
            'Content-Disposition',
            f"inline; filename*=utf-8''{dl}"
        )

    return result


@route('/fileupload', method='OPTIONS')
@allow_cross_origin
def fileupload_options():
    response.content_type = "text/plain; charset=utf-8"
    return ''


@route('/fileupload', method='POST')
@allow_cross_origin
@require_token('store')
def fileupload():
    """Upload a new original (thumbnails are derived later)."""
    thumb_p = (request.forms.get('type') == "T")
    coll = request.forms.coll
    name = request.forms.store

    if thumb_p:
        return 'Ignoring thumbnail upload!'

    bucket, key = make_s3_key(coll, False, name)
    upload = list(request.files.values())[0]
    content_type = upload.content_type or 'application/octet-stream'

    s3.put_object(Bucket=bucket, Key=key, Body=upload.file, ContentType=content_type)

    response.content_type = 'text/plain; charset=utf-8'
    return 'Ok.'


@route('/filedelete', method='POST')
@require_token('filename')
def filedelete():
    """Delete original + derived thumbnails for a collection."""
    coll = request.forms.coll
    name = request.forms.filename

    # Delete original
    bucket, orig_key = make_s3_key(coll, False, name)
    s3.delete_object(Bucket=bucket, Key=orig_key)

    # Delete matching thumbnails (prefix: basename_)
    thumb_bucket, thumb_prefix_base = make_s3_key(coll, True, '')
    base = path.splitext(name)[0] + '_'
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=thumb_bucket, Prefix=f"{thumb_prefix_base}/{base}"):
        for obj in page.get('Contents', []):
            s3.delete_object(Bucket=thumb_bucket, Key=obj['Key'])

    response.content_type = 'text/plain; charset=utf-8'
    return 'Ok.'


@route('/getmetadata')
@require_token('filename')
def getmetadata():
    """Fetch original from S3 and return EXIF metadata."""
    coll = request.query.coll
    name = request.query.filename
    bucket, key = make_s3_key(coll, False, name)
    if not metadata_slots.acquire(blocking=False):
        abort_with_reason(503, 'metadata_busy', 'Metadata processing busy; retry later',
                          **{'Retry-After': '5'})
    try:
        try:
            tags = read_metadata(s3, bucket, key,
                                 max_bytes=getattr(settings, 'METADATA_MAX_BYTES', 32*1024*1024),
                                 timeout=getattr(settings, 'METADATA_TIMEOUT_SECONDS', 10),
                                 memory_bytes=getattr(settings, 'METADATA_MEMORY_BYTES', 192*1024*1024))
        except MetadataError as exc:
            abort_with_reason(exc.status, exc.reason, 'Metadata request could not be processed')
        except ClientError as exc:
            if exc.response['Error']['Code'] in ('404', 'NoSuchKey', 'NotFound'):
                abort_with_reason(404, 'asset_not_found', 'Attachment not found')
            raise
    finally:
        metadata_slots.release()

    if request.query.get('dt') == 'date':
        try:
            response.content_type = 'text/plain; charset=utf-8'
            return str(tags['EXIF DateTimeOriginal'])
        except KeyError:
            abort_with_reason(404, 'metadata_date_not_found', 'DateTime not found in EXIF')

    out = defaultdict(dict)
    for k, v in tags.items():
        parts = k.split()
        if len(parts) < 2:
            continue
        out.setdefault(parts[0], {})[parts[1]] = str(v)

    result = [OrderedDict((('Name', k), ('Fields', f))) for k, f in out.items()]
    response.content_type = 'application/json; charset=utf-8'
    return json.dumps(result, indent=4)


@route('/testkey')
@require_token('random', always=True)
def testkey():
    response.content_type = 'text/plain; charset=utf-8'
    return 'Ok.'


@route('/web_asset_store.xml')
@include_timestamp
def web_asset_store():
    response.content_type = 'text/xml; charset=utf-8'
    return template('web_asset_store.xml', host=public_origin())


@route('/')
def main_page():
    return 'It works!'


from bottle import default_app
app = RequestLogging(default_app(), storage_backend,
                     getattr(settings, 'TRUSTED_PROXY_IPS', ()))

if __name__ == '__main__':
    from bottle import run
    run(
        app=app,
        host='0.0.0.0',
        port=settings.PORT,
        server=settings.SERVER,
        debug=settings.DEBUG,
        reloader=settings.DEBUG,
        quiet=True
    )
