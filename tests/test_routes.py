"""Exercise the real Bottle routes without a listener or AWS access."""
from io import BytesIO
import importlib
import tempfile
import unittest
from urllib.parse import urlencode
from wsgiref.util import setup_testing_defaults


class LocalRouteTests(unittest.TestCase):
    def test_download_static_reference_delete_and_missing(self):
        import settings
        with tempfile.TemporaryDirectory() as root:
            from unittest.mock import patch
            with patch.multiple(settings, STORAGE_BACKEND='local', BASE_DIR=root,
                                COLLECTION_DIRS={'example': 'example'}, KEY=None):
                server = importlib.import_module('server')
                server.s3.put_object(Bucket=root + '/example', Key='originals/a.att.jpg', Body=b'original')
                server.s3.put_object(Bucket=root + '/example', Key='thumbnails/a.att_100.jpg', Body=b'thumb')

                def request(route, values, method='GET'):
                    env = {}
                    setup_testing_defaults(env)
                    env['PATH_INFO'] = route
                    env['REQUEST_METHOD'] = method
                    encoded = urlencode(values)
                    env['QUERY_STRING'] = encoded if method == 'GET' else ''
                    env['HTTP_X_FORWARDED_PROTO'] = 'https'
                    env['wsgi.input'] = BytesIO(encoded.encode() if method == 'POST' else b'')
                    if method == 'POST':
                        env['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
                        env['CONTENT_LENGTH'] = str(len(encoded))
                    status = []
                    result = server.default_app() if hasattr(server, 'default_app') else __import__('bottle').default_app()
                    chunks = result(env, lambda s, h, exc_info=None: status.append(s))
                    try:
                        return status, b''.join(chunks)
                    finally:
                        if hasattr(chunks, 'close'):
                            chunks.close()

                values = {'coll': 'example', 'filename': 'a.att.jpg', 'type': 'O'}
                self.assertEqual(request('/fileget', values)[1], b'original')
                self.assertEqual(request('/static/example/originals/a.att.jpg', {})[1], b'original')
                self.assertIn(b'/static/example/originals/a.att.jpg', request('/getfileref', values)[1])
                self.assertEqual(request('/filedelete', values, 'POST')[1], b'Ok.')
                self.assertTrue(request('/fileget', values)[0][0].startswith('404'))
                self.assertEqual(list(server.s3.paginate(Bucket=root + '/example', Prefix='thumbnails/a.att_'))[0]['Contents'], [])
