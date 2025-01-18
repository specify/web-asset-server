#!/usr/bin/env python3

import logging
from functools import wraps
from glob import glob
from mimetypes import guess_type
from os import makedirs, path, remove
from urllib.parse import quote
from urllib.request import pathname2url
import hmac
import json
import time
from collection_definitions import COLLECTION_DIRS
from datetime import datetime
from time import sleep
from metadata_tools.metadata_tools import MetadataTools
from sh import convert
from bottle import Bottle
from image_db import ImageDb
from image_db import TIME_FORMAT

app = application = Bottle()

# Configure logging
import settings

level = logging.getLevelName(settings.LOG_LEVEL)
logging.basicConfig(filename='app.log', level=level)


from bottle import (
    Response, BaseRequest, request, response, static_file, template, abort,
    HTTPResponse)

BaseRequest.MEMFILE_MAX = 300 * 1024 * 1024

def get_image_db():
    image_db = ImageDb()
    return image_db

def log(msg):
    logging.debug(msg)

def get_rel_path(coll, thumb_p, storename):
    """Return originals or thumbnails subdirectory of the main
    attachments directory for the given collection.
    """
    type_dir = settings.THUMB_DIR if thumb_p else settings.ORIG_DIR
    first_subdir = storename[0:2]
    second_subdir = storename[2:4]
    if COLLECTION_DIRS is None:
        return path.join(type_dir, first_subdir, second_subdir)

    try:
        coll_dir = COLLECTION_DIRS[coll]
    except KeyError:
        err = f"Unknown collection: {coll}"
        log(err)
        # response.content_type = 'text/plain; charset=utf-8'
        # response.status = 403
        # response.text = err
        # log (err)
        # return response
        abort(404, "Unknown collection: %r" % coll)

    return path.join(coll_dir, type_dir, first_subdir, second_subdir)

def str2bool(value, raise_exc=False):
    """converts diverse string values into boolean True or False,
       replaces deprecated distutils and str2bool."""
    true_set = {'yes', 'true', 't', 'y', '1'}
    false_set = {'no', 'false', 'f', 'n', '0'}

    if isinstance(value, str):
        value = value.lower()
        if value in true_set:
            return True
        if value in false_set:
            return False

    if raise_exc:
        raise ValueError('Expected "%s"' % '", "'.join(true_set | false_set))
    return None



def generate_token(timestamp, filename):
    """Generate the auth token for the given filename and timestamp.
    This is for comparing to the client submited token.
    """
    timestamp = str(timestamp)
    if timestamp is None:
        log(f"Missing timestamp; token generation failure.")
    if filename is None:
        log(f"Missing filename, token generation failure.")
    mac = hmac.new(settings.KEY.encode(), timestamp.encode() + filename.encode(), digestmod='md5')
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
    log(f"Valid token: {token_in} time: {timestr}")



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
                    response.body = f"403 - forbidden. Invalid token: '{params.token}'"
                    log(response.body)
                    return response
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


def resolve_file(filename, collection, type, scale):
    """Inspect the request object to determine the file being requested.
    If the request is for a thumbnail , and it has not been generated, do
    so before returning accession_copy.
    Returns the relative path to the requested file in the base attachments directory.
    """

    thumb_p = (type == "T")
    storename = filename

    relpath = get_rel_path(collection, thumb_p, storename)

    if not thumb_p:
        return path.join(relpath, storename)
    scale = int(scale)
    basepath = path.join(settings.BASE_DIR, relpath)

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
        makedirs(basepath)

    orig_dir = path.join(settings.BASE_DIR, get_rel_path(request.query.coll, thumb_p=False, storename=storename))
    orig_path = path.join(orig_dir, storename)

    if not path.exists(orig_path):
        abort(404, "Missing original: %s" % orig_path)

    input_spec = orig_path
    convert_args = ('-resize', "%dx%d>" % (scale, scale))
    if mimetype == 'application/pdf':
        input_spec += '[0]'  # only thumbnail first page of PDF
        convert_args += ('-background', 'white', '-flatten')  # add white background to PDFs

    log("Scaling thumbnail to %d" % scale)
    convert(input_spec, *(convert_args + (scaled_pathname,)))

    return path.join(relpath, scaled_name)



@app.route('/static/<path:path>')
def static(path):
    """Serve static files to the client. Primarily for Web Portal."""
    if not settings.ALLOW_STATIC_FILE_ACCESS:
        abort(404)
    filename = path.split('/')[-1]
    image_db=get_image_db()
    records = image_db.get_image_record_by_internal_filename(filename)
    if len(records) < 1:
        log(f"Static record not found: {request.query.filename}")
        response.content_type = 'text/plain; charset=utf-8'
        response.status = 404
        return response
    if records[0]['redacted']:
        response.content_type = 'text/plain; charset=utf-8'
        response.status = 403
        log(f"Token required")
        return response

    return static_file(path, root=settings.BASE_DIR)


def getFileUrl(filename, collection, image_type, scale):
    server_name = f"{settings.SERVER_NAME}:{settings.SERVER_PORT}" if settings.OVERRIDE_PORT else settings.SERVER_NAME

    return '%s://%s/static/%s' % (settings.SERVER_PROTOCOL,
                                  server_name,
                                  pathname2url(resolve_file(filename, collection, image_type, scale))
                                  )



@app.route('/getfileref')
@allow_cross_origin
def getfileref():
    """Returns a URL to the static file indicated by the query parameters."""
    if not settings.ALLOW_STATIC_FILE_ACCESS:
        log("static file access denied")
        abort(404)
    response.content_type = 'text/plain; charset=utf-8'
    log(f"{getFileUrl(request.query.filename,request.query.coll,request.query['type'],request.query.scale)}")

    return getFileUrl(request.query.filename,
                      request.query.coll,
                      request.query['type'],
                      request.query.scale)



@app.route('/fileget')
@require_token('filename')
def fileget():
    """Returns the file data of the file indicated by the query parameters."""
    log(f"fileget {request.query.filename}")
    image_db=get_image_db()
    records = image_db.get_image_record_by_internal_filename(request.query.filename)
    log(f"Fileget complete")
    if len(records) < 1:
        log(f"Record not found: {request.query.filename}")
        response.content_type = 'text/plain; charset=utf-8'
        response.status = 404
        return response
    if records[0]['redacted']:
        log(f"Redacted, check auth token")
        try:
            # Note, we're hitting this twice with the @require_token decorator
            validate_token(request.query.token, request.query.filename)
        except TokenException as e:
            response.content_type = 'text/plain; charset=utf-8'
            response.status = 403
            response.body = f"403 - forbidden. Invalid token: '{request.query.token}'"
            log(response.body)
            return response
        log(f"Token validated for redacted record...")
    else:
        log(f"Not redacted, no check required")
    log(f"Valid request: {request.query.filename}")

    resolved_file = resolve_file(request.query.filename,
                                 request.query.coll,
                                 request.query['type'],
                                 request.query.scale)
    r = static_file(resolved_file,
                    root=settings.BASE_DIR)
    download_name = request.query.downloadname
    if download_name:
        download_name = quote(path.basename(download_name).encode('ascii', 'replace'))
        r.set_header('Content-Disposition', "inline; filename*=utf-8''%s" % download_name)
    log(f"Get complete:{request.query.filename}")
    return r


@app.route('/fileupload', method='OPTIONS')
@allow_cross_origin
def fileupload_options():
    response.content_type = "text/plain; charset=utf-8"
    return ''

@app.route('/fileupload', method='POST')
@allow_cross_origin
@require_token('store')
def fileupload():
    """Accept original file uploads and store them in the proper
    attachment subdirectory.
    """
    image_db = get_image_db()
    start_save = time.time()
    log(f"Post request for fileupload...")
    thumb_p = (request.forms['type'] == "T")
    storename = request.forms.store
    basepath = path.join(settings.BASE_DIR, get_rel_path(request.forms.coll, thumb_p, storename))

    pathname = path.join(basepath, storename)

    if len(storename) < 7:
        log(f"Name too short: {storename}")
        response.content_type = 'text/plain; charset=utf-8'
        response.status = 400
        return response
    if thumb_p:
        return 'Ignoring thumbnail upload!'
    if 'original_path' in request.forms.keys():
        response_list = image_db.get_image_record_by_original_filename(original_filename=request.forms['original_filename'],
                                                                       collection=request.forms.coll, exact=True)
    else:
        response_list = []

    upload = list(request.files.values())[0]

    log(f"Saving upload: {upload}")

    if path.isfile(pathname) or len(response_list) > 0:
        log("Duplicate file; return failure:")
        response.content_type = 'text/plain; charset=utf-8'
        response.status = 409
        return response.status

    if not path.exists(basepath):
        makedirs(basepath)

    upload.save(pathname, overwrite=True)

    response.content_type = 'text/plain; charset=utf-8'
    original_filename = None
    original_path = None
    notes = None
    redacted = False
    orig_md5 = None
    datetime_now = datetime.utcnow()
    if 'original_filename' in request.forms.keys():
        log("original filename field set")
        original_filename = request.forms['original_filename']
    else:
        notes = f"uploaded manually through specify portal at {datetime_now}"
        log("original filename field is not set")
    if 'original_path' in request.forms.keys():
        original_path = request.forms['original_path']
    if 'notes' in request.forms.keys():
        notes = request.forms['notes']
    if 'redacted' in request.forms.keys():
        redacted = str2bool(request.forms['redacted'])
    if 'datetime' in request.forms.keys():
        datetime_now = datetime.strptime(request.forms['datetime'], TIME_FORMAT)
    if 'orig_md5' in request.forms.keys():
        orig_md5 = request.forms['orig_md5']

    try:
        image_db.create_image_record(original_filename,
                                     getFileUrl(storename, request.forms.coll, 'file', 0),
                                     storename,
                                     request.forms.coll,
                                     original_path,
                                     notes,
                                     redacted,
                                     datetime_now,
                                     orig_md5)
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        abort(500, f'Unexpected error: {ex}')

    log(f"Image upload complete: original filename {original_filename} mapped to {storename}")
    end_save = time.time()
    log(f"Total time: {end_save - start_save}")
    return 'Ok.'


@app.route('/filedelete', method='POST')
@require_token('filename')
def filedelete():
    """Delete the file indicated by the query parameters. Returns 404
    if the original file does not exist. Any associated thumbnails will
    also be deleted.
    """
    image_db = get_image_db()
    storename = request.forms.filename

    basepath = path.join(settings.BASE_DIR, get_rel_path(request.forms.coll, thumb_p=False, storename=storename))
    thumbpath = path.join(settings.BASE_DIR, get_rel_path(request.forms.coll, thumb_p=True, storename=storename))

    pathname = path.join(basepath, storename)

    if not path.exists(pathname):
        abort(404)

    log("Deleting %s" % pathname)
    remove(pathname)

    prefix = storename.split('.att')[0]
    base_filename = prefix[0:prefix.rfind('.')]
    pattern = path.join(thumbpath, base_filename + '*' + prefix[prefix.rfind('.') + 1:])

    log("Deleting thumbnails matching %s" % pattern)
    for name in glob(pattern):
        remove(name)

    response.content_type = 'text/plain; charset=utf-8'
    image_db.delete_image_record(storename)
    return 'Ok.'


def json_datetime_handler(x):
    if isinstance(x, datetime):
        return x.strftime(TIME_FORMAT)
    raise TypeError("Unknown type")

# file_string can be md5 of the original file, (search_type=md5)
# the full file path or, (search_type=path)
# the filename. (search_type=filename) default if param omitted
@app.route('/getImageRecord')
@require_token('file_string', always=True)
def get_image_record():
    image_db = get_image_db()
    query_params = request.query

    search_type = query_params.get('search_type', default='filename')
    query_string = query_params.get('file_string', default='')
    exact = str2bool(query_params.get('exact', default='False'))
    collection = query_params.get('coll')

    search_functions = {
        'filename': lambda: image_db.get_image_record_by_original_filename(query_string, exact=exact,
                                                                           collection=collection),
        'path': lambda: image_db.get_image_record_by_original_path(query_string, exact=exact, collection=collection),
        'md5': lambda: image_db.get_image_record_by_original_image_md5(query_string, collection=collection)
    }

    search_function = search_functions.get(search_type)
    if not search_function:
        abort(400, 'Invalid search type')

    record_list = search_function()
    log(f"Record list: {record_list}")

    if not record_list:
        log("Image not found, returning 404")
        abort(404)

    return json.dumps(record_list, indent=4, sort_keys=True, default=json_datetime_handler)


@app.route('/getexifdata')
@require_token('filename')
def get_exif_metadata():
    """Provides access to EXIF metadata."""
    storename = request.query.filename
    basepath = path.join(settings.BASE_DIR, get_rel_path(request.query.coll, thumb_p=False, storename=storename))
    pathname = path.join(basepath, storename)
    datatype = request.query.dt
    if not path.exists(pathname):
        abort(404)

    exif_instance = MetadataTools(pathname, encoding=settings.ENCODING)
    try:
        tags = exif_instance.read_exif_tags()

    except Exception as e:
        log(f"Error reading EXIF data: {e}")
        tags = {}

    if datatype == 'date':
        try:
            return str(tags['EXIF:DateTimeOriginal'])
        except KeyError:
            abort(404, 'DateTime not found in EXIF')

    response.content_type = 'application/json'

    return json.dumps(tags, indent=4, sort_keys=True, default=json_datetime_handler)


@app.route('/updateexifdata', method='POST')
@require_token('filename')
def updateexifdata():
    """Updates EXIF metadata"""
    storename = request.forms.filename
    exif_data = request.forms.exif_dict
    exif_data = json.loads(exif_data)
    base_root = path.join(settings.BASE_DIR, get_rel_path(request.forms.coll, thumb_p=False, storename=storename))
    thumb_root = path.join(settings.BASE_DIR, get_rel_path(request.forms.coll, thumb_p=True, storename=storename))
    orig_path = path.join(base_root, storename)
    thumb_path = path.join(thumb_root, storename)
    path_list = [orig_path, thumb_path]
    for rel_path in path_list:
        if not path.exists(rel_path):
            abort(404)

        if not exif_data:
            abort(400)

        if isinstance(exif_data, dict):
            md = MetadataTools(path=rel_path, encoding=settings.ENCODING)
            try:
                md.write_exif_tags(exif_dict=exif_data)
            except:
                response.content_type = 'text/plain; charset=utf-8'
                response.status = 422
                response.body = f"422 - metadata Tag not supported: {request.query.token}"
                log(response.body)
                return response
        else:
            log(f"exif_data is not a dictionary")

        return f"{storename} updated with new exif metadata"


@app.route('/testkey')
@require_token('random', always=True)
def testkey():
    """If access to this resource succeeds, clients can conclude
    that they have a valid access key.
    """
    response.content_type = 'text/plain; charset=utf-8'
    return 'Ok.'


@app.route('/web_asset_store.xml')
@include_timestamp
def web_asset_store():
    """Serve an XML description of the URLs available here."""
    response.content_type = 'text/xml; charset=utf-8'
    return template('web_asset_store.xml', host="%s:%d" % (settings.SERVER_NAME, settings.SERVER_PORT))

@app.route('/')
def main_page():
    log("Hit root")
    return 'Specify attachment server'


if __name__ == '__main__':
    from bottle import run
    image_db = get_image_db()
    log("Starting up....")
    image_db = ImageDb()
    while image_db.connect() is not True:
        sleep(5)
        log("Retrying db connection....")
    image_db.create_tables()
    log("running server...")

    run(app=application,
        host='0.0.0.0',
        port=settings.PORT,
        server=settings.SERVER,
        debug=settings.DEBUG_APP,
        reloader=settings.DEBUG_APP
        )

    log("Exiting.")