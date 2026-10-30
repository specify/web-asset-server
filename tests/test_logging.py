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
            self.assertTrue(record['completed'])
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
