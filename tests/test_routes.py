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

                def request(route, values, method='GET', headers=None):
                    env = {}
                    setup_testing_defaults(env)
                    env['PATH_INFO'] = route
                    env['REQUEST_METHOD'] = method
                    encoded = urlencode(values)
                    env['QUERY_STRING'] = encoded if method == 'GET' else ''
                    env['HTTP_X_FORWARDED_PROTO'] = 'https'
                    env.update(headers or {})
                    env['wsgi.input'] = BytesIO(encoded.encode() if method == 'POST' else b'')
                    if method == 'POST':
                        env['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
                        env['CONTENT_LENGTH'] = str(len(encoded))
                    status = []
                    response_headers = []
                    result = server.default_app() if hasattr(server, 'default_app') else __import__('bottle').default_app()
                    def start(s, h, exc_info=None):
                        status.append(s)
                        response_headers.extend(h)
                    chunks = result(env, start)
                    try:
                        body = b''.join(chunks)
                        request.headers = dict(response_headers)
                        return status, body
                    finally:
                        if hasattr(chunks, 'close'):
                            chunks.close()

                values = {'coll': 'example', 'filename': 'a.att.jpg', 'type': 'O'}
                self.assertTrue(request('/fileget', dict(values, filename='../escape'))[0][0].startswith('400'))
                self.assertTrue(request('/fileget', dict(values, type='T', scale='bad'))[0][0].startswith('400'))
                self.assertTrue(request('/fileget', dict(values, type='T', scale='0'))[0][0].startswith('400'))
                self.assertEqual(request('/fileget', values)[1], b'original')
                self.assertIn('X-Timestamp', request.headers)
                self.assertEqual(request('/fileget', values, headers={'HTTP_RANGE': 'bytes=0-2'})[1], b'ori')
                self.assertTrue(request('/fileget', values, headers={'HTTP_RANGE': 'bytes=0-2'})[0][0].startswith('206'))
                request('/fileget', values)
                modified = request.headers['Last-Modified']
                self.assertTrue(request('/fileget', values, headers={'HTTP_IF_MODIFIED_SINCE': modified})[0][0].startswith('304'))
                self.assertEqual(request('/fileget', values, 'HEAD')[1], b'')
                with patch.multiple(settings, SERVER_NAME='assets.example.edu', SERVER_PORT=8443):
                    self.assertIn(b'https://assets.example.edu:8443/fileget', request('/web_asset_store.xml', {})[1])
                self.assertEqual(request('/static/example/originals/a.att.jpg', {})[1], b'original')
                self.assertIn(b'/static/example/originals/a.att.jpg', request('/getfileref', values)[1])
                self.assertEqual(request('/filedelete', values, 'POST')[1], b'Ok.')
                self.assertTrue(request('/fileget', values)[0][0].startswith('404'))
                self.assertEqual(list(server.s3.paginate(Bucket=root + '/example', Prefix='thumbnails/a.att_'))[0]['Contents'], [])
