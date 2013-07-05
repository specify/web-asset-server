from os import path, mkdir, remove
from mimetypes import guess_type
from sh import convert
from glob import glob
from urllib import pathname2url
from collections import defaultdict, OrderedDict
import EXIF
import json

from bottle import route, request, response, static_file, template, abort

import settings

def get_rel_path(coll, thumb_p):
    coll_dir = settings.COLLECTION_DIRS[coll]
    type_dir = settings.THUMB_DIR if thumb_p else settings.ORIG_DIR
    return path.join(coll_dir, type_dir)

def resolve_file():
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

    if mimetype == 'application/pdf':
        # use PNG for PDF thumbnails
        ext = '.png'

    scaled_name = "%s_%d%s" % (root, scale, ext)
    scaled_pathname = path.join(basepath, scaled_name)

    if path.exists(scaled_pathname):
        print "Serving previously scaled thumbnail"
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

    print "Scaling thumbnail to %d" % scale
    convert(input_spec, *(convert_args + (scaled_pathname,)))

    return path.join(relpath, scaled_name)

@route('/static/<path:path>')
def static(path):
    return static_file(path, root=settings.BASE_DIR)

@route('/getfileref')
def getfileref():
    response.set_header('Access-Control-Allow-Origin', '*')
    response.content_type = 'text/plain; charset=utf-8'
    return "http://%s:%d/static/%s" % (settings.HOST, settings.PORT,
                                       pathname2url(resolve_file()))

@route('/fileget')
def fileget():
    return static_file(resolve_file(), root=settings.BASE_DIR)

@route('/fileupload', method='POST')
def fileupload():
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
def filedelete():
    storename = request.forms.filename
    basepath = path.join(settings.BASE_DIR, get_rel_path(request.forms.coll, thumb_p=False))
    thumbpath = path.join(settings.BASE_DIR, get_rel_path(request.forms.coll, thumb_p=True))

    pathname = path.join(basepath, storename)
    if not path.exists(pathname):
        abort(404)

    print "Deleting %s" % pathname
    remove(pathname)

    prefix = storename.split('.att')[0]
    pattern = path.join(thumbpath, prefix + '*')
    print "Deleting thumbnails matching %s" % pattern
    for name in glob(pattern):
        remove(name)

    response.content_type = 'text/plain; charset=utf-8'
    return 'Ok.'

@route('/getmetadata')
def getmetadata():
    storename = request.query.filename
    basepath = path.join(settings.BASE_DIR, get_rel_path(request.query.coll, thumb_p=False))
    pathname = path.join(basepath, storename)
    datatype = request.query.dt

    if not path.exists(pathname):
        abort(404)

    with open(pathname, 'rb') as f:
        try:
            tags = EXIF.process_file(f)
        except:
            print "Error reading exif data."
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

@route('/web_asset_store.xml')
def web_asset_store():
    response.content_type = 'text/xml; charset=utf-8'
    return template('web_asset_store.xml', host="%s:%d" % (settings.HOST, settings.PORT))

if __name__ == '__main__':
    from bottle import run
    run(host='0.0.0.0', port=settings.PORT, debug=settings.DEBUG, server=settings.SERVER)
