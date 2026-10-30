import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from manage_collection_dirs import update_config


class ConfigAtomicityTests(unittest.TestCase):
    def test_chown_failure_preserves_original_and_removes_temporary(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'settings_local.py'
            source = "KEY = 'private'\nCOLLECTION_DIRS = {}\n"
            target.write_text(source)
            with patch('manage_collection_dirs.os.chown', side_effect=PermissionError):
                with self.assertRaisesRegex(ValueError, 'sudo'):
                    update_config(target, 'local', 'add', ['example'])
            self.assertEqual(target.read_text(), source)
            self.assertEqual(list(Path(directory).iterdir()), [target])

    def test_missing_local_mapping_does_not_switch_shared_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'settings_local.py'
            source = "KEY = 'private'\n"
            target.write_text(source)
            with self.assertRaisesRegex(ValueError, 'Shared local storage'):
                update_config(target, 'local', 'add', ['example'])
            self.assertEqual(target.read_text(), source)
            update_config(target, 's3', 'add', ['example', 's3://bucket/example'])
            self.assertIn('COLLECTION_S3_PATHS', target.read_text())
