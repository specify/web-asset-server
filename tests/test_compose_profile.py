"""Validate actual Compose interpolation without starting containers."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('docker'), 'Docker Compose CLI required')
class ComposeProfileTests(unittest.TestCase):
    def test_unset_dotenv_and_exported_profile(self):
        try:
            subprocess.run(['docker', 'compose', 'version'], check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=10)
        except (subprocess.SubprocessError, FileNotFoundError):
            self.skipTest('Docker Compose plugin required')
        for dotenv, exported, expected in [('', None, None), ('AWS_PROFILE=institution\n', None, 'institution'), ('AWS_PROFILE=institution\n', 'host-profile', 'host-profile')]:
            with self.subTest(dotenv=dotenv, exported=exported), tempfile.TemporaryDirectory() as directory:
                envfile = Path(directory) / '.env'
                envfile.write_text(dotenv)
                environment = dict(os.environ)
                environment.pop('AWS_PROFILE', None)
                environment.pop('COMPOSE_FILE', None)
                if exported is not None:
                    environment['AWS_PROFILE'] = exported
                result = subprocess.check_output(
                    ['docker', 'compose', '--env-file', str(envfile),
                     '-f', str(ROOT / 'docker-compose.yml'), '-f', str(ROOT / 'compose.s3.yml'),
                     'config', '--format', 'json'], env=environment, text=True, timeout=15)
                values = json.loads(result)['services']['asset-server']['environment']
                self.assertEqual(values.get('AWS_PROFILE'), expected)
                # Compose config retains an unresolved pass-through as null;
                # Compose omits that variable from the container environment.
