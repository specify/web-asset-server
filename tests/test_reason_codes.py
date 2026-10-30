import unittest
from unittest.mock import patch
import server
from bottle import request, HTTPError
from app_logging import abort_with_reason


class ReasonCodeTests(unittest.TestCase):
    def test_auth_reasons_do_not_contain_credentials(self):
        with patch.object(server.settings, 'KEY', 'test-secret'), patch.object(server.settings, 'TIME_TOLERANCE', 600), patch.object(server, 'get_timestamp', return_value=10000):
            for token, reason in [('', 'missing_token'), ('bad', 'malformed_token'), ('bad:abc', 'malformed_token'), ('bad:1', 'expired_token'), ('bad:10000', 'invalid_token')]:
                with self.assertRaises(server.TokenException) as caught:
                    server.validate_token(token, 'image.jpg')
                self.assertEqual(caught.exception.reason, reason)
                self.assertNotIn('test-secret', caught.exception.reason)

    def test_reason_is_attached_to_request(self):
        request.bind({})
        with self.assertRaises(HTTPError) as caught:
            abort_with_reason(404, 'asset_not_found', 'Attachment not found')
        self.assertEqual(caught.exception.status_code, 404)
        self.assertEqual(request.environ['asset.error_reason'], 'asset_not_found')

    def test_local_static_escape_is_not_an_internal_error(self):
        import tempfile
        from storage import LocalStorage
        with tempfile.TemporaryDirectory() as root, patch.object(server, 'storage_backend', 'local'), patch.object(server, 's3', LocalStorage()), patch.object(server.settings, 'BASE_DIR', root), patch.object(server.settings, 'ALLOW_STATIC_FILE_ACCESS', True):
            request.bind({})
            with self.assertRaises(HTTPError) as caught:
                server.static_handler('../../etc/passwd')
            self.assertEqual(caught.exception.status_code, 404)
            self.assertEqual(request.environ['asset.error_reason'], 'invalid_static_path')

    def test_https_discovery_never_advertises_internal_listener(self):
        import xml.etree.ElementTree as ET
        from urllib.parse import urlsplit
        request.bind({'REQUEST_METHOD': 'GET', 'HTTP_X_FORWARDED_PROTO': 'https'})
        with patch.object(server.settings, 'SERVER_NAME', 'assets.example.edu'), patch.object(server.settings, 'SERVER_PORT', 443), patch.object(server.settings, 'PORT', 8080):
            root = ET.fromstring(server.web_asset_store())
        self.assertEqual(len(root), 5)
        for endpoint in root:
            parsed = urlsplit(endpoint.text)
            self.assertEqual(parsed.scheme, 'https')
            self.assertEqual(parsed.hostname, 'assets.example.edu')
            self.assertIsNone(parsed.port)
