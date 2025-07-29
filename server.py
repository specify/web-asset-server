from collections import defaultdict, OrderedDict
from functools import wraps
from glob import glob
from mimetypes import guess_type
from os import path, mkdir
from urllib.parse import quote
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
    Response, request, response, abort,
    route, HTTPResponse, static_file, template)

# Initialize S3 client
s3 = boto3.client('s3')
BUCKET = settings.S3_BUCKET
PREFIX = settings.S3_PREFIX.rstrip('/')


def log(msg):
    if settings.DEBUG:
        print(msg)


def get_rel_path(coll, thumb_p):
    """Return the collection subdirectory for originals or thumbnails."""
    type_dir = settings.THUMB_DIR if thumb_p else settings.ORIG_DIR
    if settings.COLLECTION_DIRS is None:
        return type_dir
    try:
        coll_dir = settings.COLLECTION_DIRS[coll]
    except KeyError:
        abort(404, f"Unknown collection: {coll!r}")
    return path.join(coll_dir, type_dir)


def make_s3_key(relpath, filename=''):
    """Build a POSIX-style S3 key under optional PREFIX."""
    key = relpath.replace(path.sep, '/')
    if filename:
        key = f"{key}/{filename}" if key else filename
    if PREFIX:
        key = f"{PREFIX}/{key}" if key else PREFIX
    return key.lstrip('/')


def generate_token(timestamp, filename):
    """Generate the auth token for the given filename and timestamp.
    This is for comparing to the client submited token.
    """
    timestamp = str(timestamp)
    mac = hmac.new(
        settings.KEY.encode(),
        timestamp.encode() + filename.encode(),
        'md5'
    )
    return f"{mac.hexdigest()}:{timestamp}"


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
        now = get_timestamp()
        if abs(now - timestamp) >= settings.TIME_TOLERANCE:
            raise TokenException("Auth token timestamp out of range.")
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
            if always or request.method not in ('GET','HEAD') or settings.REQUIRE_KEY_FOR_GET:
                params = request.forms if request.method=='POST' else request.query
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
            r.set_header('Access-Control-Allow-Origin','*')
            raise
        target = result if isinstance(result, Response) else response
        target.set_header('Access-Control-Allow-Origin','*')
        return result
    return wrapper


def resolve_s3_key():
    thumb_p = (request.query.get('type')=='T')
    coll = request.query.coll
    name = request.query.filename
    rel = get_rel_path(coll, thumb_p)

    if not thumb_p:
        return make_s3_key(rel, name)

    # thumbnail: check cache, else generate
    scale = int(request.query.scale)
    root, ext = path.splitext(name)
    if ext.lower() in ('.pdf','.tiff','.tif'):
        ext = '.png'
    thumb_name = f"{root}_{scale}{ext}"
    thumb_key = make_s3_key(rel, thumb_name)

    # cached?
    try:
        s3.head_object(Bucket=BUCKET, Key=thumb_key)
        log(f"Cached thumbnail: {thumb_key}")
        return thumb_key
    except ClientError as e:
        if e.response['Error']['Code'] not in ('404','NoSuchKey'):
            raise

    # fetch original
    orig_key = make_s3_key(get_rel_path(coll, False), name)
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=orig_key)
    except ClientError as e:
        code = e.response['Error']['Code']
        if code in ('404','NoSuchKey'):
            abort(404, f"Missing original: {orig_key}")
        raise
    data = obj['Body'].read()

    # write temp files
    from tempfile import gettempdir
    tmp = gettempdir()
    local_in = path.join(tmp, name)
    local_out = path.join(tmp, thumb_name)
    with open(local_in,'wb') as f:
        f.write(data)

    args = ['-resize', f"{scale}x{scale}>"]
    if obj['ContentType']=='application/pdf':
        args += ['-background','white','-flatten']
        local_in += '[0]'
    convert(local_in, *args, local_out)

    # upload thumbnail
    ctype, _ = guess_type(local_out)
    with open(local_out,'rb') as f:
        s3.put_object(
            Bucket=BUCKET,
            Key=thumb_key,
            Body=f,
            ContentType=ctype or 'application/octet-stream'
        )
    return thumb_key


def stream_s3_object(key):
    try:
        obj = s3.get_object(Bucket=BUCKET, Key=key)
    except ClientError as e:
        if e.response['Error']['Code'] in ('404','NoSuchKey'):
            abort(404, f"Missing object: {key}")
        raise
    return obj['Body'].read(), obj['ContentType']


@route('/static/<path:path>')
def static(path):
    """Serve static files to the client. Primarily for Web Portal."""
    if not settings.ALLOW_STATIC_FILE_ACCESS:
        abort(404)
    return static_file(path, root=settings.BASE_DIR)


@route('/getfileref')
@allow_cross_origin
def getfileref():
    """Returns a URL to the static file indicated by the query parameters."""
    if not settings.ALLOW_STATIC_FILE_ACCESS:
        abort(404)
    response.content_type='text/plain; charset=utf-8'
    key = resolve_s3_key()
    return f"http://{settings.HOST}:{settings.PORT}/static/{quote(key)}"


@route('/fileget')
@require_token('filename')
def fileget():
    key = resolve_s3_key()
    data, ctype = stream_s3_object(key)
    r = Response(body=data)
    r.content_type = ctype
    dl = request.query.get('downloadname')
    if dl:
        dl = quote(path.basename(dl).encode('ascii','replace'))
        r.set_header('Content-Disposition', f"inline; filename*=utf-8''{dl}")
    return r


@route('/fileupload', method='OPTIONS')
@allow_cross_origin
def fileupload_options():
    response.content_type='text/plain; charset=utf-8'
    return ''


@route('/fileupload', method='POST')
@allow_cross_origin
@require_token('store')
def fileupload():
    thumb_p = (request.forms['type']=='T')
    coll = request.forms.coll
    name = request.forms.store
    key = make_s3_key(get_rel_path(coll, thumb_p), name)
    upload = list(request.files.values())[0]
    body = upload.file.read()
    ctype = upload.content_type or 'application/octet-stream'
    s3.put_object(Bucket=BUCKET, Key=key, Body=body, ContentType=ctype)
    response.content_type='text/plain; charset=utf-8'
    return 'Ok.'


@route('/filedelete', method='POST')
@require_token('filename')
def filedelete():
    coll = request.forms.coll
    name = request.forms.filename
    orig_key = make_s3_key(get_rel_path(coll,False), name)
    s3.delete_object(Bucket=BUCKET, Key=orig_key)
    # delete thumbnails
    thumb_prefix = make_s3_key(get_rel_path(coll,True), '')
    base = name.split('.',1)[0] + '_'
    paginator = s3.get_paginator('list_objects_v2')
    for page in paginator.paginate(Bucket=BUCKET, Prefix=thumb_prefix+base):
        for obj in page.get('Contents',[]):
            s3.delete_object(Bucket=BUCKET, Key=obj['Key'])
    response.content_type='text/plain; charset=utf-8'
    return 'Ok.'


@route('/getmetadata')
@require_token('filename')
def getmetadata():
    coll = request.query.coll
    name = request.query.filename
    key = make_s3_key(get_rel_path(coll,False), name)
    data, _ = stream_s3_object(key)
    f = BytesIO(data)
    try:
        tags = exifread.process_file(f)
    except:
        log("Error reading EXIF data.")
        tags = {}
    if request.query.dt=='date':
        try:
            return str(tags['EXIF DateTimeOriginal'])
        except KeyError:
            abort(404,'DateTime not found in EXIF')
    out = defaultdict(dict)
    for k,v in tags.items():
        parts=k.split()
        if len(parts)<2: continue
        out.setdefault(parts[0],{})[parts[1]] = str(v)
    result = [OrderedDict((('Name',k),('Fields',f))) for k,f in out.items()]
    response.content_type='application/json'
    return json.dumps(result, indent=4)


@route('/testkey')
def testkey():
    response.content_type='text/plain; charset=utf-8'
    return 'Ok.'


@route('/web_asset_store.xml')
@include_timestamp
def web_asset_store():
    response.content_type='text/xml; charset=utf-8'
    return template('web_asset_store.xml', host=f"{settings.SERVER_NAME}:{settings.SERVER_PORT}")


@route('/')
def main_page():
    return 'It works!'


if __name__=='__main__':
    from bottle import run
    run(host='0.0.0.0', port=settings.PORT,
        server=settings.SERVER, debug=settings.DEBUG,
        reloader=settings.DEBUG)