from os import path, mkdir
from mimetypes import guess_type
from sh import convert

from bottle import route, request, response, static_file, template, abort

import settings

def get_path(coll, thumb_p):
    coll_dir = settings.COLLECTION_DIRS[coll]
    type_dir = settings.THUMB_DIR if thumb_p else settings.ORIG_DIR
    return path.join(settings.BASE_DIR, coll_dir, type_dir)

@route('/fileget')
def fileget():
    thumb_p = (request.query['type'] == "T")
    storename = request.query.filename
    basepath = get_path(request.query.coll, thumb_p)
    pathname = path.join(basepath, storename)

    if not thumb_p:
        return static_file(pathname, root='/')

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
        return static_file(scaled_pathname, root='/')

    if not path.exists(basepath):
        mkdir(basepath)

    orig_path = path.join(get_path(request.query.coll, False), storename)

    if not path.exists(orig_path):
        abort(404, "Missing original: %s" % orig_path)

    input_spec = orig_path
    convert_args = ('-resize', "%dx%d>" % (scale, scale))
    if mimetype == 'application/pdf':
        input_spec += '[0]'     # only thumbnail first page of PDF
        convert_args += ('-background', 'white', '-flatten')  # add white background to PDFs

    print "Scaling thumbnail to %d" % scale
    convert(input_spec, *(convert_args + (scaled_pathname,)))

    return static_file(scaled_pathname, root='/')

@route('/fileupload', method='POST')
def fileupload():
    thumb_p = (request.forms['type'] == "T")
    storename = request.forms.store
    basepath = get_path(request.forms.coll, thumb_p)
    pathname = path.join(basepath, storename)

    if thumb_p:
        return 'Ignoring thumbnail upload!'

    if not path.exists(basepath):
        mkdir(basepath)

    upload = request.files.values()[0]
    upload.save(pathname, overwrite=True)

    response.content_type = 'text/plain; charset=utf-8'
    return 'Ok.'

@route('/web_asset_store.xml')
def web_asset_store():
    response.content_type = 'text/xml; charset=utf-8'
    return template('web_asset_store.xml', host=settings.HOST)

if __name__ == '__main__':
    from bottle import run
    run(host='0.0.0.0', port=3088, debug=True, reloader=True)
