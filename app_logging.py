"""JSON application logs without request secrets or exception values."""
from contextvars import ContextVar
from datetime import datetime, timezone
import json
import logging
import sys
import time
import traceback
import uuid
from ipaddress import ip_address
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


class RedactedErrorStream:
    """Keep raw WSGI tracebacks out of stderr; structured errors retain context."""
    def __init__(self):
        self.reported = False

    def write(self, text):
        if text and not self.reported:
            logger.error('wsgi_error')
            self.reported = True
        return len(text)

    def flush(self):
        pass


class RequestLogging:
    def __init__(self, application, backend, trusted_proxy_ips=()):
        self.application = application
        self.backend = backend
        self.trusted_proxy_ips = {str(ip_address(value)) for value in trusted_proxy_ips}

    def __call__(self, environ, start_response):
        environ = dict(environ)
        environ['wsgi.errors'] = RedactedErrorStream()
        identifier = uuid.uuid4().hex
        token = request_id.set(identifier)
        started = time.monotonic()
        status = 500
        count = 0
        completed = False
        streaming_error = False
        result = None
        def start(value, headers, exc_info=None):
            nonlocal status
            status = int(value.split()[0])
            headers = [(k,v) for k,v in headers if k.lower() != 'x-request-id']
            headers.append(('X-Request-ID', identifier))
            write = start_response(value, headers, exc_info)
            def counted_write(data):
                nonlocal count
                result = write(data)
                count += len(data)
                return result
            return counted_write
        try:
            result = self.application(environ, start)
            for chunk in result:
                count += len(chunk)
                yield chunk
            completed = True
        except Exception:
            streaming_error = True
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
                peer = environ.get('REMOTE_ADDR', '')
                try:
                    peer = str(ip_address(peer))
                except ValueError:
                    peer = None
                client = peer
                if peer in self.trusted_proxy_ips:
                    # nginx must overwrite this header, never append client input.
                    try:
                        client = str(ip_address(environ.get('HTTP_X_REAL_IP', '')))
                    except ValueError:
                        pass
                if client:
                    fields['client_ip'] = client
                agent = environ.get('HTTP_USER_AGENT', '')
                if agent:
                    fields['user_agent'] = ''.join(c for c in agent[:512] if c.isprintable())
                reason = environ.get('asset.error_reason')
                if reason:
                    fields['reason'] = reason
                elif status >= 400:
                    fields['reason'] = {400: 'bad_request', 403: 'forbidden', 404: 'not_found', 416: 'invalid_range'}.get(status, 'internal_error' if status >= 500 else 'request_rejected')
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
                level = logging.ERROR if streaming_error or status >= 500 else logging.WARNING if status >= 400 or not completed else logging.INFO
                is_healthcheck = (
                    environ.get('REMOTE_ADDR') in ('127.0.0.1', '::1')
                    and environ.get('HTTP_USER_AGENT') == 'SpecifyAssetHealthcheck/1.0'
                    and environ.get('REQUEST_METHOD') == 'GET'
                    and fields['route'] == '/web_asset_store.xml'
                    and not environ.get('QUERY_STRING')
                )
                if is_healthcheck:
                    fields['healthcheck'] = True
                if not (is_healthcheck and status == 200 and completed and not streaming_error):
                    logger.log(level, 'request_finished', extra={'fields': fields})
                request_id.reset(token)


def abort_with_reason(status, reason, message):
    from bottle import request, abort
    request.environ['asset.error_reason'] = reason
    abort(status, message)
