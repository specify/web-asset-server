from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from storage import LocalStorage, create_storage
from unittest.mock import Mock, patch


class StorageTests(unittest.TestCase):
    def test_local_roundtrip_and_thumbnail_cleanup(self):
        with tempfile.TemporaryDirectory() as root:
            store = LocalStorage()
            store.put_object(Bucket=root, Key='originals/a.att.jpg', Body=b'original')
            store.put_object(Bucket=root, Key='thumbnails/a.att_100.jpg', Body=b'thumb')
            store.put_object(Bucket=root, Key='thumbnails/other_100.jpg', Body=b'other')
            with store.get_object(Bucket=root, Key='originals/a.att.jpg')['Body'] as body:
                self.assertEqual(body.read(), b'original')
            pages = list(store.paginate(Bucket=root, Prefix='thumbnails/a.att_'))
            self.assertEqual(pages[0]['Contents'], [{'Key': 'thumbnails/a.att_100.jpg'}])
            store.delete_object(Bucket=root, Key='originals/a.att.jpg')
            self.assertFalse(store._path(root, 'originals/a.att.jpg').exists())
            with self.assertRaises(ValueError):
                store.put_object(Bucket=root, Key='../escape', Body=b'bad')

    def test_local_selection_does_not_initialize_aws(self):
        store, backend = create_storage(SimpleNamespace(STORAGE_BACKEND='local'))
        self.assertIsInstance(store, LocalStorage)
        self.assertEqual(backend, 'local')

    def test_s3_selection_uses_configured_client(self):
        client = Mock()
        boto3 = SimpleNamespace(client=Mock(return_value=client))
        with patch.dict('sys.modules', boto3=boto3):
            store, backend = create_storage(SimpleNamespace(
                STORAGE_BACKEND='s3', COLLECTION_S3_PATHS={'c': 's3://bucket/c'}))
        self.assertIs(store, client)
        self.assertEqual(backend, 's3')
        boto3.client.assert_called_once_with('s3')

    def test_default_is_local_even_with_s3_mappings(self):
        store, backend = create_storage(SimpleNamespace(
            COLLECTION_S3_PATHS={'c': 's3://bucket/c'}))
        self.assertIsInstance(store, LocalStorage)
        self.assertEqual(backend, 'local')

    def test_local_upload_is_readable_by_backup_tools(self):
        import stat
        from storage import LocalStorage
        with tempfile.TemporaryDirectory() as root:
            LocalStorage().put_object(Bucket=root, Key='originals/test.jpg', Body=b'asset')
            self.assertEqual(stat.S_IMODE((Path(root) / 'originals/test.jpg').stat().st_mode), 0o644)
