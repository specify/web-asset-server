import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from manage_collection_dirs import update_config


class ConfigurationTests(unittest.TestCase):
    def test_environment_then_private_file(self):
        with tempfile.TemporaryDirectory() as directory:
            shutil.copy('settings.py', directory)
            Path(directory, 'settings_local.py').write_text(
                "HOST = 'private.example.edu'\nKEY = 'private'\nSERVER_PORT = 443\n")
            env = dict(os.environ, SERVER_NAME='env.example.edu', ATTACHMENT_KEY='env', SERVER_PORT='8080')
            subprocess.run([sys.executable, '-c',
                "import settings; assert settings.SERVER_NAME == 'private.example.edu'; "
                "assert settings.KEY == 'private'; assert settings.SERVER_PORT == 443; "
                "assert settings.STORAGE_BACKEND == 'local'"],cwd=directory,env=env,check=True)

    def test_collection_editor_preserves_private_values(self):
        with tempfile.TemporaryDirectory() as directory:
            filename = Path(directory, 'settings_local.py')
            filename.write_text("KEY = 'private'\nCOLLECTION_DIRS = {}\nCOLLECTION_S3_PATHS = {}\n")
            filename.chmod(0o640)
            update_config(filename, 'local', 'add', ['fish'])
            update_config(filename, 's3', 'add', ["O'Brien", 's3://bucket/prefix'])
            result = {}; exec(filename.read_text(), result)
            self.assertEqual(result['KEY'], 'private')
            self.assertEqual(filename.stat().st_mode & 0o777, 0o640)
            self.assertEqual(result['COLLECTION_DIRS'], {'fish': 'fish'})
            self.assertEqual(result['COLLECTION_S3_PATHS'], {"O'Brien": 's3://bucket/prefix'})
            update_config(filename, 's3', 'remove', ["O'Brien"])
            result = {}; exec(filename.read_text(), result)
            self.assertEqual(result['COLLECTION_S3_PATHS'], {})

    def test_public_https_port_never_inherits_internal_listener(self):
        for local_source in ['', "HOST = 'assets.example.edu'\nPORT = 9000\n"]:
            with tempfile.TemporaryDirectory() as directory:
                shutil.copy('settings.py', directory)
                Path(directory, 'settings_local.py').write_text(local_source)
                env = dict(os.environ)
                env.pop('SERVER_PORT', None)
                env['PORT'] = '8080'
                subprocess.run([sys.executable, '-c',
                    "import settings; assert settings.SERVER_PORT == 443; "
                    "assert settings.PORT in (8080, 9000)"], cwd=directory, env=env, check=True)

    def test_shared_example_explicitly_uses_public_https_port(self):
        with tempfile.TemporaryDirectory() as directory:
            shutil.copy('settings.py', directory)
            shutil.copy('settings_local.example.py', Path(directory, 'settings_local.py'))
            subprocess.run([sys.executable, '-c',
                "import settings; assert settings.SERVER_PORT == 443; assert settings.PORT == 8080"],
                cwd=directory, check=True)
