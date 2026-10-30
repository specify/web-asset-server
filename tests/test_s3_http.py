from io import BytesIO
import unittest
from unittest.mock import Mock
from bottle import request
from s3_http import ObjectBody, serve_s3, object_headers


class StreamingTests(unittest.TestCase):
    def test_botocore_last_modified_timezone(self):
        from datetime import datetime
        from dateutil.tz import tzutc
        result = object_headers({'LastModified':datetime(2026,10,29,tzinfo=tzutc())})
        self.assertEqual(result['Last-Modified'], 'Thu, 29 Oct 2026 00:00:00 GMT')

    def test_bounded_reads_and_early_close(self):
        body = Mock()
        body.read.side_effect = [b'x', b'']
        iterator = ObjectBody(body)
        self.assertEqual(list(iterator), [b'x'])
        body.read.assert_called_with(65536)
        body.close.assert_called_once()
        iterator = ObjectBody(Mock())
        iterator.close()  # Even a response never iterated must release the connection.
        iterator.body.close.assert_called_once()

    def test_read_failure_closes(self):
        body = Mock(); body.read.side_effect = IOError('disconnected')
        with self.assertRaises(IOError): next(ObjectBody(body))
        body.close.assert_called_once()

    def test_head_ranges_and_if_range(self):
        for value, expected, status in [
                ('bytes=2-4', 'bytes=2-4', 206),
                ('bytes=7-', 'bytes=7-9', 206),
                ('bytes=-3', 'bytes=7-9', 206),
                ('bytes=2-999', 'bytes=2-9', 206),
                ('bytes=20-', None, 416), ('bytes=-0', None, 416),
                ('bytes=5-2', None, 416), ('bytes=bad', None, 416),
                ('bytes=0-1,4-5', None, 200)]:
            with self.subTest(value=value):
                request.bind({'REQUEST_METHOD':'GET', 'HTTP_RANGE':value})
                client = Mock(); client.head_object.return_value = {'ContentLength':10, 'ETag':'"v1"'}
                client.get_object.return_value = {'Body':BytesIO(b'abc'), 'ContentLength':3,
                                                  'ContentRange':'bytes 2-4/10'}
                result = serve_s3(client,'bucket','key')
                self.assertEqual(result.status_code,status)
                if status == 416:
                    client.get_object.assert_not_called()
                    self.assertEqual(result.headers['Content-Range'],'bytes */10')
                else:
                    args={'Bucket':'bucket','Key':'key'}
                    if expected: args.update(Range=expected,IfMatch='"v1"')
                    client.get_object.assert_called_once_with(**args)
                    result.body.close()
        request.bind({'REQUEST_METHOD':'HEAD','HTTP_RANGE':'bytes=0-2'})
        client = Mock(); client.head_object.return_value={'ContentLength':10}
        result=serve_s3(client,'bucket','key')
        self.assertEqual(result.headers['Content-Length'],'10')
        client.get_object.assert_not_called()
        request.bind({'REQUEST_METHOD':'GET','HTTP_RANGE':'bytes=0-2','HTTP_IF_RANGE':'"old"'})
        client=Mock(); client.head_object.return_value={'ContentLength':10,'ETag':'"new"'}
        client.get_object.return_value={'Body':BytesIO(b'full')}
        result=serve_s3(client,'bucket','key')
        self.assertEqual(result.status_code,200)
        client.get_object.assert_called_once_with(Bucket='bucket',Key='key')
        result.body.close()
