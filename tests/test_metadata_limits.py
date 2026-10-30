from io import BytesIO
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch
from metadata_reader import read_metadata, MetadataError


class MetadataLimitsTests(unittest.TestCase):
    def test_declared_and_actual_oversize_inputs_close_body_without_parser(self):
        for declared in (0, 100):
            body = BytesIO(b'x'*20)
            client = Mock()
            client.get_object.return_value = dict(Body=body, ContentLength=declared)
            with patch('metadata_reader.subprocess.run') as parser:
                with self.assertRaises(MetadataError) as caught:
                    read_metadata(client, 'bucket', 'key', max_bytes=10)
                self.assertEqual(caught.exception.reason, 'metadata_input_too_large')
                parser.assert_not_called()
                self.assertTrue(body.closed)

    def test_parser_timeout_is_bounded_and_body_closed(self):
        body = BytesIO(b'data')
        client = Mock()
        client.get_object.return_value = dict(Body=body)
        with patch('metadata_reader.subprocess.run', side_effect=subprocess.TimeoutExpired('parser', 1)) as parser:
            with self.assertRaises(MetadataError) as caught:
                read_metadata(client, 'b', 'k', timeout=1)
            self.assertEqual(caught.exception.reason, 'metadata_timeout')
            self.assertEqual(parser.call_args.kwargs['timeout'], 1)
            self.assertFalse(__import__('pathlib').Path(parser.call_args.args[0][-2]).exists())
        self.assertTrue(body.closed)

    @unittest.skipUnless(sys.platform == 'linux', 'Address-space limits are validated on the Linux deployment runtime')
    def test_real_isolated_parser_accepts_non_exif_input(self):
        client = Mock()
        client.get_object.return_value = dict(Body=BytesIO(b'not an image'))
        self.assertEqual(read_metadata(client, 'b', 'k'), {})

    def test_busy_metadata_route_does_not_download(self):
        import server
        from bottle import request, HTTPError
        from threading import BoundedSemaphore
        slots = BoundedSemaphore(1)
        slots.acquire()
        request.bind({'REQUEST_METHOD': 'GET', 'QUERY_STRING': 'coll=c&filename=image.jpg'})
        with patch.object(server, 'metadata_slots', slots), patch.object(server, 'make_s3_key', return_value=('b', 'k')), patch.object(server, 'read_metadata') as reader, patch.object(server.settings, 'REQUIRE_KEY_FOR_GET', False):
            with self.assertRaises(HTTPError) as caught:
                server.getmetadata()
            self.assertEqual(caught.exception.status_code, 503)
            self.assertEqual(caught.exception.get_header('Retry-After'), '5')
            reader.assert_not_called()
        slots.release()

    def test_metadata_rejection_releases_slot(self):
        import server
        from bottle import request, HTTPError
        from threading import BoundedSemaphore
        slots = BoundedSemaphore(1)
        request.bind({'REQUEST_METHOD': 'GET', 'QUERY_STRING': 'coll=c&filename=image.jpg'})
        with patch.object(server, 'metadata_slots', slots), patch.object(server, 'make_s3_key', return_value=('b', 'k')), patch.object(server, 'read_metadata', side_effect=MetadataError(413, 'metadata_input_too_large')), patch.object(server.settings, 'REQUIRE_KEY_FOR_GET', False):
            with self.assertRaises(HTTPError) as caught:
                server.getmetadata()
            self.assertEqual(caught.exception.status_code, 413)
            self.assertEqual(request.environ['asset.error_reason'], 'metadata_input_too_large')
        self.assertTrue(slots.acquire(blocking=False))
        slots.release()
