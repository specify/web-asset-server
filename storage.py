"""Storage clients used by the shared attachment routes."""
from io import BytesIO
from mimetypes import guess_type
from pathlib import Path


class LocalStorage:
    """Filesystem implementation of the object operations used by the server."""

    def _path(self, bucket, key):
        root = Path(bucket).resolve()
        target = (root / key).resolve()
        if target != root and root not in target.parents:
            raise ValueError('Attachment path escapes collection root')
        return target

    def head_object(self, *, Bucket, Key):
        target = self._path(Bucket, Key)
        if not target.is_file():
            from botocore.exceptions import ClientError
            raise ClientError({'Error': {'Code': '404'}}, 'HeadObject')
        return {'ContentLength': target.stat().st_size}

    def get_object(self, *, Bucket, Key):
        self.head_object(Bucket=Bucket, Key=Key)
        target = self._path(Bucket, Key)
        return {'Body': target.open('rb'),
                'ContentType': guess_type(str(target))[0] or 'application/octet-stream'}

    def put_object(self, *, Bucket, Key, Body, ContentType=None):
        target = self._path(Bucket, Key)
        target.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        import os
        from tempfile import NamedTemporaryFile
        temporary = None
        try:
            with NamedTemporaryFile(dir=target.parent, delete=False) as output:
                temporary = output.name
                if hasattr(Body, 'read'):
                    shutil.copyfileobj(Body, output)
                else:
                    output.write(Body)
            # Match normal attachment readability for shared-volume tools.
            os.chmod(temporary, 0o644)
            os.replace(temporary, target)
        finally:
            if temporary:
                Path(temporary).unlink(missing_ok=True)

    def delete_object(self, *, Bucket, Key):
        self._path(Bucket, Key).unlink(missing_ok=True)

    def get_paginator(self, operation):
        if operation != 'list_objects_v2':
            raise ValueError(operation)
        return self

    def paginate(self, *, Bucket, Prefix):
        root = Path(Bucket).resolve()
        parent = self._path(Bucket, Prefix).parent
        yield {'Contents': [{'Key': str(p.relative_to(root))}
                            for p in parent.glob('*') if p.is_file()
                            and str(p.relative_to(root)).startswith(Prefix)]}


def create_storage(settings):
    backend = getattr(settings, 'STORAGE_BACKEND', 'local')
    if backend == 'local':
        return LocalStorage(), backend
    if backend == 's3':
        import boto3
        return boto3.client('s3'), backend
    raise ValueError('STORAGE_BACKEND must be local or s3')
