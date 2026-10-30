from io import BytesIO
from pathlib import Path
import importlib
import unittest
from unittest.mock import Mock, patch
from bottle import request
from botocore.exceptions import ClientError
import settings
import shutil
import subprocess
import tempfile


class ThumbnailTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('convert'), 'ImageMagick is required')
    def test_pr35_multilayer_tiff_first_page_and_single_output(self):
        with patch.object(settings, 'STORAGE_BACKEND', 'local'):
            server = importlib.import_module('server')
        from storage import LocalStorage
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory, 'originals', 'multilayer.att.tiff')
            source.parent.mkdir()
            subprocess.run(['convert', '-size', '64x48', 'xc:red',
                            '-size', '64x48', 'xc:blue', str(source)], check=True,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            request.bind({'REQUEST_METHOD':'GET', 'QUERY_STRING':
                          'coll=example&type=T&scale=24&filename=multilayer.att.tiff'})
            with patch.object(server, 's3', LocalStorage()), \
                    patch.object(server, 'storage_backend', 'local'), \
                    patch.multiple(settings, BASE_DIR=directory, COLLECTION_DIRS=None):
                bucket, key = server.resolve_s3_key()
                self.assertEqual(server.resolve_s3_key(), (bucket, key))
            thumbnail = Path(bucket, key)
            self.assertEqual([p.name for p in thumbnail.parent.iterdir()], ['multilayer.att_24.png'])
            pixel = subprocess.check_output(['convert', str(thumbnail), '-depth', '8', 'RGB:-'],
                                            stderr=subprocess.PIPE)
            self.assertEqual(pixel[:3], b'\xff\x00\x00')  # First red layer, not second blue.

    def test_first_page_is_used_and_temporary_files_removed(self):
        with patch.object(settings, 'STORAGE_BACKEND', 'local'):
            server = importlib.import_module('server')
        for extension in ('pdf', 'tiff', 'heic'):
            with self.subTest(extension=extension):
                name = 'test.att.' + extension
                request.bind({'REQUEST_METHOD':'GET', 'QUERY_STRING':
                              'coll=c&type=T&scale=24&filename=' + name})
                client = Mock()
                client.head_object.side_effect = ClientError({'Error':{'Code':'404'}}, 'HeadObject')
                body = BytesIO(b'original')
                client.get_object.return_value = {'Body':body}
                inputs=[]
                def convert(*args, **kwargs):
                    self.assertEqual(args[:3], ('-limit', 'thread', '1'))
                    source = next(arg for arg in args if arg.endswith('[0]'))
                    inputs.append(source)
                    self.assertTrue(source.endswith('[0]'))
                    Path(args[-1]).write_bytes(b'png')
                with patch.object(server,'s3',client), patch.object(server,'storage_backend','s3'), \
                        patch.object(settings,'COLLECTION_S3_PATHS',{'c':'s3://bucket/c'}), \
                        patch.object(server,'convert',convert):
                    self.assertEqual(server.resolve_s3_key(),('bucket','c/thumbnails/test.att_24.png'))
                self.assertTrue(body.closed)
                self.assertFalse(Path(inputs[0][:-3]).parent.exists())
                client.put_object.assert_called_once()

    def test_busy_generation_rejects_without_downloading_and_cached_still_works(self):
        from threading import BoundedSemaphore
        from bottle import HTTPError, response
        server = importlib.import_module('server')
        slots = BoundedSemaphore(1)
        slots.acquire()
        client = Mock()
        request.bind({'REQUEST_METHOD': 'GET', 'QUERY_STRING': 'coll=c&type=T&scale=24&filename=image.jpg'})
        response.bind()
        with patch.object(settings, 'THUMBNAIL_QUEUE_WAIT_SECONDS', 0), patch.object(server, 'thumbnail_slots', slots), patch.object(server, 's3', client), patch.object(server, 'make_s3_key', return_value=('bucket', 'thumb')):
            client.head_object.side_effect = ClientError({'Error': {'Code': '404'}}, 'HeadObject')
            with self.assertRaises(HTTPError) as caught:
                server.resolve_s3_key()
            self.assertEqual(caught.exception.status_code, 503)
            self.assertEqual(caught.exception.get_header('Retry-After'), '5')
            self.assertEqual(request.environ['asset.error_reason'], 'thumbnail_busy')
            client.get_object.assert_not_called()
            client.head_object.side_effect = None
            self.assertEqual(server.resolve_s3_key(), ('bucket', 'thumb'))
        slots.release()

    def test_failure_releases_generation_slot(self):
        from threading import BoundedSemaphore
        server = importlib.import_module('server')
        slots = BoundedSemaphore(1)
        client = Mock()
        client.head_object.side_effect = ClientError({'Error': {'Code': '404'}}, 'HeadObject')
        client.get_object.side_effect = RuntimeError('storage unavailable')
        request.bind({'REQUEST_METHOD': 'GET', 'QUERY_STRING': 'coll=c&type=T&scale=24&filename=image.jpg'})
        with patch.object(settings, 'THUMBNAIL_QUEUE_WAIT_SECONDS', 0), patch.object(server, 'thumbnail_slots', slots), patch.object(server, 's3', client), patch.object(server, 'make_s3_key', return_value=('bucket', 'thumb')):
            with self.assertRaises(RuntimeError):
                server.resolve_s3_key()
        self.assertTrue(slots.acquire(blocking=False))
        slots.release()
