"""Bound metadata downloads and isolate EXIF parsing from the web process."""
from contextlib import closing
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory


class MetadataError(Exception):
    def __init__(self, status, reason):
        self.status = status
        self.reason = reason


def read_metadata(client, bucket, key, *, max_bytes=32*1024*1024,
                  timeout=10, memory_bytes=192*1024*1024):
    obj = client.get_object(Bucket=bucket, Key=key)
    with closing(obj['Body']) as body, TemporaryDirectory(prefix='asset-metadata-') as directory:
        if obj.get('ContentLength', 0) > max_bytes:
            raise MetadataError(413, 'metadata_input_too_large')
        source = Path(directory) / 'original'
        total = 0
        with source.open('wb') as output:
            while True:
                chunk = body.read(min(64*1024, max_bytes-total+1))
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise MetadataError(413, 'metadata_input_too_large')
                output.write(chunk)
        try:
            result = subprocess.run(
                [sys.executable, '-I', str(Path(__file__).with_name('metadata_worker.py')),
                 str(source), str(memory_bytes)], stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, timeout=timeout, check=False)
        except subprocess.TimeoutExpired:
            raise MetadataError(504, 'metadata_timeout') from None
        if result.returncode:
            raise MetadataError(422, 'metadata_parse_failed')
        try:
            value = json.loads(result.stdout)
            if not isinstance(value, dict) or not all(isinstance(k, str) and isinstance(v, str) for k,v in value.items()):
                raise ValueError()
            return value
        except (ValueError, UnicodeError):
            raise MetadataError(422, 'metadata_parse_failed') from None
