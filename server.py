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
    scale = request.query.get('scale', None)
    scale = int(scale) if scale is not None else None
    mimetype, encoding = guess_type(storename)

    if thumb_p and scale is not None and mimetype in settings.CAN_THUMBNAIL:

        if not path.exists(pathname):
            abort(404)

        root, ext = path.splitext(storename)
        scaled_name = "%s_%d%s" % (root, scale, ext)
        scaled_pathname = path.join(basepath, scaled_name)

        if not path.exists(scaled_pathname):
            output_file = 'png:' + scaled_pathname if mimetype == 'application/pdf' else scaled_pathname
            convert(pathname, '-resize', "%dx%d>" % (scale, scale), output_file)

        pathname = scaled_pathname

    send_mimetype = 'image/png' if mimetype == 'application/pdf' and thumb_p else 'auto'

    return static_file(pathname, root='/', mimetype=send_mimetype)

@route('/fileupload', method='POST')
def fileupload():
    thumb_p = (request.forms['type'] == "T")
    storename = request.forms.store
    basepath = get_path(request.forms.coll, thumb_p)
    pathname = path.join(basepath, storename)
    mimetype, encoding = guess_type(storename)

    if thumb_p:
        return 'Ignoring thumbnail upload!'

    if not path.exists(basepath):
        mkdir(basepath)

    upload = request.files.values()[0]
    upload.save(pathname, overwrite=True)
    resp = 'Ok.'

    if mimetype in settings.CAN_THUMBNAIL:
        thumb_basepath = get_path(request.forms.coll, thumb_p=True)
        thumbpath = path.join(thumb_basepath, storename)

        if not path.exists(thumb_basepath):
            mkdir(thumb_basepath)

        output_file = thumbpath
        input_file = pathname
        if mimetype == 'application/pdf':
            output_file = 'png:' + output_file
            input_file += '[0]'

        convert(input_file, '-resize' , '%s>' % settings.THUMB_SIZE, '-background', 'white', '-flatten', output_file)
        resp += ' Thumbnail generated.'

    response.content_type = 'text/plain; charset=utf-8'
    return resp

@route('/web_asset_store.xml')
def web_asset_store():
    response.content_type = 'text/xml; charset=utf-8'
    return template('web_asset_store.xml', host=settings.HOST)

if __name__ == '__main__':
    from bottle import run
    run(host='0.0.0.0', port=8080, debug=True, reloader=True)
