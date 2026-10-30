"""JSON application logs without request secrets or exception values."""
from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import sys
import time
import traceback
import uuid
from urllib.parse import parse_qs

request_id = ContextVar('request_id', default=None)
logger = logging.getLogger('asset_server')


class JsonFormatter(logging.Formatter):
    def format(self, record):
        event = {'timestamp': datetime.now(timezone.utc).isoformat(),
                 'level': record.levelname, 'event': record.getMessage(),
                 'request_id': request_id.get()}
        event.update(getattr(record, 'fields', {}))
        if record.exc_info and record.exc_info[0]:
            event['error_type'] = record.exc_info[0].__name__
            # Omit exception messages, source lines and locals: SDK errors can
            # contain URLs, object names or authentication material.
            event['traceback'] = [{'file': frame.filename, 'line': frame.lineno,
                                   'function': frame.name}
                                  for frame in traceback.extract_tb(record.exc_info[2])]
        return json.dumps(event)


def configure_logging(level='INFO'):
    level = level.upper()
    if level not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
        raise ValueError('Invalid LOG_LEVEL')
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    # Paste otherwise logs full URLs, including authentication query strings.
    logging.getLogger('wsgi').disabled = True


class RequestLogging:
    def __init__(self, application, backend):
        self.application = application
        self.backend = backend

    def __call__(self, environ, start_response):
        identifier = uuid.uuid4().hex
        token = request_id.set(identifier)
        started = time.monotonic()
        status = 500
        count = 0
        completed = False
        result = None
        def start(value, headers, exc_info=None):
            nonlocal status
            status = int(value.split()[0])
            headers = [(k,v) for k,v in headers if k.lower() != 'x-request-id']
            headers.append(('X-Request-ID', identifier))
            return start_response(value, headers, exc_info)
        try:
            result = self.application(environ, start)
            for chunk in result:
                count += len(chunk)
                yield chunk
            completed = True
        except Exception:
            logger.exception('request_failed')
            raise
        finally:
            try:
                if result is not None and hasattr(result, 'close'):
                    result.close()
            finally:
                route = environ.get('bottle.route')
                fields = dict(method=environ.get('REQUEST_METHOD'),
                              route=getattr(route, 'rule', 'unmatched'),
                              status=status, bytes_sent=count,
                              duration_ms=round((time.monotonic()-started)*1000, 2),
                              response_completed=completed,
                              outcome=('transfer_incomplete' if not completed else
                                       'not_found' if status == 404 else
                                       'server_error' if status >= 500 else
                                       'client_error' if status >= 400 else
                                       'redirect' if status >= 300 else 'success'))
                if fields['route'] in ('/fileget', '/getmetadata', '/getfileref'):
                    try:
                        query = parse_qs(environ.get('QUERY_STRING', ''), max_num_fields=100)
                    except ValueError:
                        query = {}
                    # Explicit allowlist: never log the raw URL, tokens or headers.
                    for source, field in (('coll', 'collection'), ('filename', 'filename')):
                        if query.get(source):
                            fields[field] = query[source][0][:1024]
                    if fields['route'] != '/getmetadata':
                        fields['asset_type'] = 'thumbnail' if query.get('type', [''])[0] == 'T' else 'original'
                elif fields['route'] == '/static/<path:path>':
                    path = environ.get('PATH_INFO', '').removeprefix('/static/')
                    collection, separator, filename = path.partition('/')
                    if separator:
                        fields.update(collection=collection[:1024], filename=filename[:1024])
                level = logging.ERROR if status >= 500 else logging.WARNING if status >= 400 or not completed else logging.INFO
                logger.log(level, 'request_finished', extra={'fields': fields})
                request_id.reset(token)
