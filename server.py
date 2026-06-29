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
from sh import convert
import boto3
from botocore.exceptions import ClientError

import settings
from bottle import (
    Response, request, response, static_file, template, abort,
    HTTPResponse, route, redirect
)


from bottle import error

@error(500)
def show_500(exc):
    import traceback
    tb = traceback.format_exc()
    print(tb)                 # prints in your console
    return "<h1>500 Internal Server Error</h1><pre>" + tb + "</pre>"


# S3 client (shared)
s3 = boto3.client('s3')


def log(msg):
    print(msg)
    # if getattr(settings, "DEBUG", False):
    #     print(msg)

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
    pass


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
        raise TokenException("Auth token is missing or malformed.")
    mac_in, timestr = token_in.split(':', 1)
    try:
        timestamp = int(timestr)
    except ValueError:
        raise TokenException("Auth token is malformed.")
    if settings.TIME_TOLERANCE is not None:
        current_time = get_timestamp()
        if not abs(current_time - timestamp) < settings.TIME_TOLERANCE:
            raise TokenException(
                "Auth token timestamp out of range: %s vs %s" % (timestamp, current_time)
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
        @wraps(func)
        def wrapper(*args, **kwargs):
            if always or request.method not in ('GET', 'HEAD') or settings.REQUIRE_KEY_FOR_GET:
                params = request.forms if request.method == 'POST' else request.query
                try:
                    validate_token(params.token, params.get(filename_param))
                except TokenException as e:
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
        result = func(*args, **kwargs)
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
    try:
        s3_uri = settings.COLLECTION_S3_PATHS[coll]
    except KeyError:
        abort(404, f"Unknown collection: {coll!r}")
    try:
        return parse_s3_uri(s3_uri)
    except ValueError as e:
        abort(500, str(e))


def make_s3_key(coll, thumb, filename=''):
    """
    Build bucket and key for given collection, thumb/orig, and filename.
    """
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
            abort(404, f"Missing object: {key}")
        raise
    return obj['Body'].read(), obj.get('ContentType', 'application/octet-stream')


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
    scale = int(request.query.scale)
    root, ext = path.splitext(name)
    if ext.lower() in ('.pdf', '.tiff', '.tif'):
        ext = '.png'
    thumb_name = f"{root}_{scale}{ext}"
    bucket, thumb_key = make_s3_key(coll, True, thumb_name)

    # If thumbnail exists, return it
    try:
        s3.head_object(Bucket=bucket, Key=thumb_key)
        log(f"Serving cached thumbnail {thumb_key}")
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
            abort(404, f"Missing original: {orig_key}")
        raise
    data = obj['Body'].read()

    # Write temp files for ImageMagick processing
    from tempfile import gettempdir
    tmp = gettempdir()
    local_orig = path.join(tmp, name)
    local_thumb = path.join(tmp, thumb_name)
    with open(local_orig, 'wb') as f:
        f.write(data)

    convert_args = ['-resize', f"{scale}x{scale}>"]
    if obj.get('ContentType', '') == 'application/pdf':
        convert_args += ['-background', 'white', '-flatten']
        local_orig_with_page = local_orig + '[0]'
    else:
        local_orig_with_page = local_orig

    log(f"Scaling thumbnail to {scale}")
    convert(local_orig_with_page, *convert_args, local_thumb)

    # Upload generated thumbnail
    ctype, _ = guess_type(local_thumb)
    with open(local_thumb, 'rb') as f:
        s3.put_object(
            Bucket=bucket,
            Key=thumb_key,
            Body=f,
            ContentType=ctype or 'application/octet-stream'
        )

    return bucket, thumb_key


### Routes ###
@route('/static/<path:path>')
def static_handler(path):
    """Serve local static files (unchanged)."""
    if not settings.ALLOW_STATIC_FILE_ACCESS:
        abort(404)

    parts = path.split('/', 1)
    if len(parts) != 2:
        abort(404, f"Bad static path: {path!r}")

    coll, rest = parts
    try:
        bucket, base_prefix = parse_s3_uri(settings.COLLECTION_S3_PATHS[coll])
    except KeyError:
        abort(404, f"Unknown collection: {coll!r}")

    key = '/'.join(p for p in (base_prefix, rest) if p)
    data, ctype = stream_s3_object(bucket, key)

    response.content_type = ctype
    return data


@route('/getfileref')
@allow_cross_origin
def getfileref():
    """Return the fileget URL for the requested attachment (client will append token etc)."""
    if not settings.ALLOW_STATIC_FILE_ACCESS:
        abort(404)

    coll = request.query.coll
    filename = request.query.filename

    # URL-encode the “collection/filename” into a single static path
    static_path = f"{quote(coll)}/{quote(filename)}"
    url = f"http://{settings.HOST}:{settings.PORT}/static/{static_path}"

    response.content_type = 'text/plain; charset=utf-8'
    return url


@route('/fileget')
@require_token('filename')
def fileget():
    bucket, key = resolve_s3_key()
    data, content_type = stream_s3_object(bucket, key)

    response.content_type = content_type

    download_name = request.query.get('downloadname')
    if download_name:
        dl = quote(path.basename(download_name).encode('ascii', 'replace'))
        response.set_header(
            'Content-Disposition',
            f"inline; filename*=utf-8''{dl}"
        )

    return data


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
    body = upload.file.read()
    content_type = upload.content_type or 'application/octet-stream'

    s3.put_object(Bucket=bucket, Key=key, Body=body, ContentType=content_type)

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
    base = name.split('.', 1)[0] + '_'
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=thumb_bucket, Prefix=f"{thumb_prefix_base}{base}"):
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
    data, _ = stream_s3_object(bucket, key)
    f = BytesIO(data)
    try:
        tags = exifread.process_file(f)
    except Exception as e:
        log(f"Error reading EXIF data: {e}")
        tags = {}

    if request.query.get('dt') == 'date':
        try:
            response.content_type = 'text/plain; charset=utf-8'
            return str(tags['EXIF DateTimeOriginal'])
        except KeyError:
            abort(404, 'DateTime not found in EXIF')

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
    protocol = request.headers.get('X-Forwarded-Proto', request.urlparts.scheme)
    return template('web_asset_store.xml', host=f"{protocol}://{settings.SERVER_NAME}")


@route('/')
def main_page():
    return 'It works!'


if __name__ == '__main__':
    from bottle import run
    run(
        host='0.0.0.0',
        port=settings.PORT,
        server=settings.SERVER,
        debug=settings.DEBUG,
        reloader=settings.DEBUG
    )
