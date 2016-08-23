from os import path, mkdir, remove
from mimetypes import guess_type
from sh import convert
from glob import glob
from urllib import pathname2url, quote
from collections import defaultdict, OrderedDict
from functools import wraps
import exifread, json, hmac, time
import sys

from bottle import (
    Response, request, response, static_file, template, abort,
    HTTPError, HTTPResponse, route, hook)

import settings

def log(msg):
    if settings.DEBUG:
        print msg

def get_rel_path(coll, thumb_p):
    """Return originals or thumbnails subdirectory of the main
    attachments directory for the given collection.
    """
    type_dir = settings.THUMB_DIR if thumb_p else settings.ORIG_DIR

    if settings.COLLECTION_DIRS is None:
        return type_dir

    try:
        coll_dir = settings.COLLECTION_DIRS[coll]
    except KeyError:
        abort(404, "Unknown collection: %r" % coll)

    return path.join(coll_dir, type_dir)

def generate_token(timestamp, filename):
    """Generate the auth token for the given filename and timestamp.
    This is for comparing to the client submited token.
    """
    timestamp = str(timestamp)
    mac = hmac.new(settings.KEY, timestamp + filename)
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
    if token_in == '':
        raise TokenException("Auth token is missing.")
    if ':' not in token_in:
        raise TokenException("Auth token is malformed.")

    mac_in, timestr = token_in.split(':')
    try:
        timestamp = int(timestr)
    except ValueError:
        raise TokenException("Auth token is malformed.")

    if settings.TIME_TOLERANCE is not None:
        current_time = get_timestamp()
        if not abs(current_time - timestamp) < settings.TIME_TOLERANCE:
            raise TokenException("Auth token timestamp out of range: %s vs %s" % (timestamp, current_time))

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
                    response.content_type = 'text/plain; charset=utf-8'
                    response.status = 403
                    return e
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
        (result if isinstance(result, Response) else response) \
                .set_header('X-Timestamp', str(get_timestamp()))
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

        (result if isinstance(result, Response) else response) \
                .set_header('Access-Control-Allow-Origin', '*')
        return result
    return wrapper

def resolve_file():
    """Inspect the request object to determine the file being requested.
    If the request is for a thumbnail and it has not been generated, do
    so before returning.

    Returns the relative path to the requested file in the base
    attachments directory.
    """
    thumb_p = (request.query['type'] == "T")
    storename = request.query.filename
    relpath = get_rel_path(request.query.coll, thumb_p)

    if not thumb_p:
        return path.join(relpath, storename)

    basepath = path.join(settings.BASE_DIR, relpath)

    scale = int(request.query.scale)
    mimetype, encoding = guess_type(storename)

    assert mimetype in settings.CAN_THUMBNAIL

    root, ext = path.splitext(storename)

    if mimetype in ('application/pdf', 'image/tiff'):
        # use PNG for PDF thumbnails
        ext = '.png'

    scaled_name = "%s_%d%s" % (root, scale, ext)
    scaled_pathname = path.join(basepath, scaled_name)

    if path.exists(scaled_pathname):
        log("Serving previously scaled thumbnail")
        return path.join(relpath, scaled_name)

    if not path.exists(basepath):
        mkdir(basepath)

    orig_dir = path.join(settings.BASE_DIR, get_rel_path(request.query.coll, thumb_p=False))
    orig_path = path.join(orig_dir, storename)

    if not path.exists(orig_path):
        abort(404, "Missing original: %s" % orig_path)

    input_spec = orig_path
    convert_args = ('-resize', "%dx%d>" % (scale, scale))
    if mimetype == 'application/pdf':
        input_spec += '[0]'     # only thumbnail first page of PDF
        convert_args += ('-background', 'white', '-flatten')  # add white background to PDFs

    log("Scaling thumbnail to %d" % scale)
    convert(input_spec, *(convert_args + (scaled_pathname,)))

    return path.join(relpath, scaled_name)

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
    response.content_type = 'text/plain; charset=utf-8'
    return "http://%s:%d/static/%s" % (settings.HOST, settings.PORT,
                                       pathname2url(resolve_file()))
@route('/fileget')
@require_token('filename')
def fileget():
    """Returns the file data of the file indicated by the query parameters."""
    r = static_file(resolve_file(), root=settings.BASE_DIR)
    download_name = request.query.downloadname
    if download_name:
        download_name = quote(path.basename(download_name))
        r.set_header('Content-Disposition', "inline; filename*=utf-8''%s" % download_name)
    return r

@route('/fileupload', method='OPTIONS')
@allow_cross_origin
def fileupload_options():
    response.content_type = "text/plain; charset=utf-8"
    return ''

@route('/fileupload', method='POST')
@allow_cross_origin
@require_token('store')
def fileupload():
    """Accept original file uploads and store them in the proper
    attchment subdirectory.
    """
    thumb_p = (request.forms['type'] == "T")
    storename = request.forms.store
    basepath = path.join(settings.BASE_DIR, get_rel_path(request.forms.coll, thumb_p))
    pathname = path.join(basepath, storename)

    if thumb_p:
        return 'Ignoring thumbnail upload!'

    if not path.exists(basepath):
        mkdir(basepath)

    upload = request.files.values()[0]
    upload.save(pathname, overwrite=True)

    response.content_type = 'text/plain; charset=utf-8'
    return 'Ok.'

@route('/filedelete', method='POST')
@require_token('filename')
def filedelete():
    """Delete the file indicated by the query parameters. Returns 404
    if the original file does not exist. Any associated thumbnails will
    also be deleted.
    """
    storename = request.forms.filename
    basepath = path.join(settings.BASE_DIR, get_rel_path(request.forms.coll, thumb_p=False))
    thumbpath = path.join(settings.BASE_DIR, get_rel_path(request.forms.coll, thumb_p=True))

    pathname = path.join(basepath, storename)
    if not path.exists(pathname):
        abort(404)

    log("Deleting %s" % pathname)
    remove(pathname)

    prefix = storename.split('.att')[0]
    pattern = path.join(thumbpath, prefix + '*')
    log("Deleting thumbnails matching %s" % pattern)
    for name in glob(pattern):
        remove(name)

    response.content_type = 'text/plain; charset=utf-8'
    return 'Ok.'

@route('/getmetadata')
@require_token('filename')
def getmetadata():
    """Provides access to EXIF metadata."""
    storename = request.query.filename
    basepath = path.join(settings.BASE_DIR, get_rel_path(request.query.coll, thumb_p=False))
    pathname = path.join(basepath, storename)
    datatype = request.query.dt

    if not path.exists(pathname):
        abort(404)

    with open(pathname, 'rb') as f:
        try:
            tags = exifread.process_file(f)
        except:
            log("Error reading exif data.")
            tags = {}

    if datatype == 'date':
        try:
            return str(tags['EXIF DateTimeOriginal'])
        except KeyError:
            abort(404, 'DateTime not found in EXIF')

    data = defaultdict(dict)
    for key, value in tags.items():
        parts = key.split()
        if len(parts) < 2: continue
        try:
            v = str(value).decode('ascii', 'replace').encode('utf-8')
        except TypeError:
            v = repr(value)

        data[parts[0]][parts[1]] = str(v)

    response.content_type = 'application/json'
    data = [OrderedDict( (('Name', key), ('Fields', value)) )
            for key,value in data.items()]

    return json.dumps(data, indent=4)

@route('/testkey')
@require_token('random', always=True)
def testkey():
    """If access to this resource succeeds, clients can conclude
    that they have a valid access key.
    """
    response.content_type ='text/plain; charset=utf-8'
    return 'Ok.'

@route('/web_asset_store.xml')
@include_timestamp
def web_asset_store():
    """Serve an XML description of the URLs available here."""
    response.content_type = 'text/xml; charset=utf-8'
    return template('web_asset_store.xml', host="%s:%d" % (settings.HOST, settings.PORT))

if __name__ == '__main__':
    from bottle import run
    sys.stderr.write("web externally identified as http://%s:%d/ from ENV\n" % (settings.HOST, settings.PORT))
    run(host='0.0.0.0', port=8080, server=settings.SERVER,
        debug=settings.DEBUG, reloader=settings.DEBUG)
