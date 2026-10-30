from io import StringIO
import json
import logging
import unittest
from app_logging import RequestLogging, JsonFormatter, logger


class LoggingTests(unittest.TestCase):
    def test_request_summary_excludes_secrets_and_counts_stream(self):
        output=StringIO(); handler=logging.StreamHandler(output)
        handler.setFormatter(JsonFormatter()); logger.addHandler(handler)
        previous=logger.level; logger.setLevel(logging.INFO)
        headers=[]
        def application(env,start):
            start('200 OK', [('Content-Type','text/plain')])
            return iter([b'ab', b'cd'])
        try:
            body=RequestLogging(application,'s3')(
                {'REQUEST_METHOD':'GET','QUERY_STRING':'token=private',
                 'HTTP_AUTHORIZATION':'secret', 'PATH_INFO':'/private-name'},
                lambda status,h,exc_info=None:headers.extend(h))
            self.assertEqual(b''.join(body),b'abcd')
            record=json.loads(output.getvalue())
            self.assertEqual(record['bytes_sent'],4)
            self.assertTrue(record['response_completed'])
            self.assertEqual(dict(headers)['X-Request-ID'],record['request_id'])
            self.assertNotIn('private',output.getvalue())
            self.assertNotIn('secret',output.getvalue())
        finally:
            logger.removeHandler(handler); logger.setLevel(previous)

    def test_exception_messages_are_not_logged(self):
        try:
            raise ValueError('credential=private')
        except ValueError:
            import sys
            record=logging.LogRecord('asset_server',logging.ERROR,__file__,1,
                                     'request_error',(),sys.exc_info())
        result=JsonFormatter().format(record)
        self.assertIn('ValueError',result)
        self.assertNotIn('credential',result)
        self.assertNotIn('private',result)

    def test_asset_fields_are_allowlisted(self):
        from types import SimpleNamespace
        output = StringIO()
        handler = logging.StreamHandler(output)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        previous = logger.level
        logger.setLevel(logging.INFO)
        def application(env, start):
            env['bottle.route'] = SimpleNamespace(rule='/fileget')
            start('200 OK', [])
            return [b'asset']
        try:
            for kind, expected in [('T', 'thumbnail'), ('O', 'original')]:
                output.seek(0); output.truncate()
                env = {'REQUEST_METHOD': 'GET', 'QUERY_STRING':
                       'coll=Example+Collection&filename=image.jpg&type=' + kind + '&token=PRIVATE_TOKEN&other=PRIVATE_VALUE'}
                list(RequestLogging(application, 's3')(env, lambda *args: None))
                record = json.loads(output.getvalue())
                self.assertEqual(record['collection'], 'Example Collection')
                self.assertEqual(record['filename'], 'image.jpg')
                self.assertEqual(record['asset_type'], expected)
                self.assertNotIn('backend', record)
                self.assertNotIn('PRIVATE', output.getvalue())
        finally:
            logger.removeHandler(handler)
            logger.setLevel(previous)

    def test_http_errors_are_distinct_from_completed_transfers(self):
        output = StringIO()
        handler = logging.StreamHandler(output)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        previous = logger.level
        logger.setLevel(logging.INFO)
        try:
            for status, outcome, level in [(200, 'success', 'INFO'), (404, 'not_found', 'WARNING'), (403, 'client_error', 'WARNING'), (500, 'server_error', 'ERROR')]:
                output.seek(0); output.truncate()
                def application(env, start):
                    start(str(status) + ' Response', [])
                    return [b'response body']
                list(RequestLogging(application, 's3')({'REQUEST_METHOD': 'GET'}, lambda *args: None))
                record = json.loads(output.getvalue())
                self.assertEqual(record['status'], status)
                self.assertEqual(record['outcome'], outcome)
                self.assertEqual(record['level'], level)
                self.assertTrue(record['response_completed'])
                self.assertNotIn('completed', record)
        finally:
            logger.removeHandler(handler)
            logger.setLevel(previous)

    def test_wsgi_write_and_yield_both_count(self):
        output = StringIO()
        handler = logging.StreamHandler(output)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
        previous = logger.level
        logger.setLevel(logging.INFO)
        written = []
        def application(env, start):
            write = start('200 OK', [])
            write(b'ab')
            return [b'cd']
        try:
            body = RequestLogging(application, 's3')({}, lambda *args: written.append)
            self.assertEqual(b''.join(body), b'cd')
            self.assertEqual(written, [b'ab'])
            self.assertEqual(json.loads(output.getvalue())['bytes_sent'], 4)
        finally:
            logger.removeHandler(handler)
            logger.setLevel(previous)
