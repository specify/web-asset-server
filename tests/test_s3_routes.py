from io import BytesIO
import importlib
import unittest
from unittest.mock import patch
from urllib.parse import urlencode
from wsgiref.util import setup_testing_defaults
from botocore.stub import Stubber
import boto3
import settings


class S3RouteTests(unittest.TestCase):
    def test_read_delete_and_authentication(self):
        with patch.object(settings, 'STORAGE_BACKEND', 'local'):
            server = importlib.import_module('server')
        client = boto3.client('s3', region_name='us-east-1',
                              aws_access_key_id='test', aws_secret_access_key='test')
        with Stubber(client) as stub, patch.object(server, 's3', client), \
                patch.object(server, 'storage_backend', 's3'), \
                patch.multiple(settings, KEY='test-key', REQUIRE_KEY_FOR_GET=False,
                               COLLECTION_S3_PATHS={'fish': 's3://bucket/fish'}):
            def request(route, values, method='GET'):
                env = {}; setup_testing_defaults(env)
                encoded = urlencode(values).encode()
                env.update(PATH_INFO=route, REQUEST_METHOD=method)
                env['QUERY_STRING'] = encoded.decode() if method == 'GET' else ''
                env['wsgi.input'] = BytesIO(encoded if method == 'POST' else b'')
                env['CONTENT_LENGTH'] = str(len(encoded)) if method == 'POST' else '0'
                env['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'
                status = []; headers = []
                def start(s,h,exc_info=None): status.append(s); headers.extend(h)
                result = __import__('bottle').default_app()(env,start)
                try: return status[0], dict(headers), b''.join(result)
                finally:
                    if hasattr(result,'close'): result.close()
            stub.add_response('get_object', {'Body': BytesIO(b'asset'), 'ContentType':'image/png'},
                              {'Bucket':'bucket','Key':'fish/originals/a.att.png'})
            values = dict(coll='fish', filename='a.att.png', type='O')
            status, headers, body = request('/fileget',values)
            self.assertEqual(body,b'asset'); self.assertIn('X-Timestamp',headers)
            status, headers, body = request('/filedelete',values,'POST')
            self.assertTrue(status.startswith('403')); self.assertIn('X-Timestamp',headers)
            stub.add_response('delete_object',{}, {'Bucket':'bucket','Key':'fish/originals/a.att.png'})
            stub.add_response('list_objects_v2', {'Contents':[{'Key':'fish/thumbnails/a.att_100.png'}]},
                              {'Bucket':'bucket','Prefix':'fish/thumbnails/a.att_'})
            stub.add_response('delete_object',{}, {'Bucket':'bucket','Key':'fish/thumbnails/a.att_100.png'})
            values['token']=server.generate_token(server.get_timestamp(),'a.att.png')
            self.assertEqual(request('/filedelete',values,'POST')[2],b'Ok.')
            stub.assert_no_pending_responses()
