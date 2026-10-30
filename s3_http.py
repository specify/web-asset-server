from app_logging import abort_with_reason
"""Bounded S3 response bodies and HTTP byte-range handling."""
import re
from datetime import timezone
from email.utils import format_datetime
from bottle import HTTPResponse, abort, request
from botocore.exceptions import ClientError


class ObjectBody:
    def __init__(self, body):
        self.body = body
        self.closed = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.closed:
            raise StopIteration
        try:
            chunk = self.body.read(64 * 1024)
            if chunk:
                return chunk
        except BaseException:
            self.close()
            raise
        self.close()
        raise StopIteration

    def close(self):
        if not self.closed:
            self.closed = True
            self.body.close()


def serve_s3(client, bucket, key):
    args = dict(Bucket=bucket, Key=key)
    try:
        # HEAD must never fetch the object body. Range GET needs its size first.
        ranged = request.headers.get('Range') if request.method == 'GET' else None
        metadata = client.head_object(**args) if request.method == 'HEAD' or ranged else None
        if metadata is not None and request.method == 'HEAD':
            return HTTPResponse(body='', headers=object_headers(metadata))
        selected = None
        if ranged:
            size = metadata['ContentLength']
            validator = request.headers.get('If-Range')
            modified = metadata.get('LastModified')
            date = format_datetime(modified.astimezone(timezone.utc), usegmt=True) if modified else None
            if validator and validator not in (metadata.get('ETag'), date):
                ranged = None
            if ranged and ',' not in ranged and ranged.startswith('bytes='):
                match = re.fullmatch(r'bytes=(\d*)-(\d*)', ranged)
                if match and any(match.groups()):
                    first, last = match.groups()
                    start = int(first) if first else max(0, size - int(last))
                    end = min(int(last), size - 1) if first and last else size - 1
                    if start <= end and start < size and (first or int(last) > 0):
                        selected = (start, end)
                if selected is None:
                    return HTTPResponse(status=416, headers={
                        'Content-Range': f'bytes */{size}', 'Accept-Ranges': 'bytes'})
            # Unsupported range units and multipart ranges get a full response.
            if selected:
                args['Range'] = f'bytes={selected[0]}-{selected[1]}'
                if metadata.get('ETag'):
                    args['IfMatch'] = metadata['ETag']
        obj = client.get_object(**args)
    except ClientError as exc:
        code = exc.response['Error']['Code']
        if code in ('404', 'NoSuchKey', 'NotFound'):
            abort_with_reason(404, 'asset_not_found', 'Attachment not found')
        if code in ('PreconditionFailed', '412'):
            abort_with_reason(412, 'asset_changed', 'Attachment changed; retry the request')
        raise
    headers = object_headers(obj)
    if selected:
        headers['Content-Range'] = obj['ContentRange']
    return HTTPResponse(body=ObjectBody(obj['Body']), status=206 if selected else 200,
                        headers=headers)


def object_headers(obj):
    headers = {'Content-Type': obj.get('ContentType', 'application/octet-stream'),
               'Accept-Ranges': 'bytes'}
    if 'ContentLength' in obj:
        headers['Content-Length'] = str(obj['ContentLength'])
    if 'ETag' in obj:
        headers['ETag'] = obj['ETag']
    if 'LastModified' in obj:
        headers['Last-Modified'] = format_datetime(obj['LastModified'].astimezone(timezone.utc), usegmt=True)
    return headers
