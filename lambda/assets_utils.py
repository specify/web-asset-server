# assets_utils.py

import hmac
import time
import os
from assets_settings import (
    KEY, TIME_TOLERANCE, COLLECTION_DIRS, THUMB_DIR, ORIG_DIR
)

def get_timestamp():
    return int(time.time())

def generate_token(timestamp, filename):
    timestamp = str(timestamp)
    mac = hmac.new(KEY.encode(), (timestamp + filename).encode(), 'md5')
    return ':'.join((mac.hexdigest(), timestamp))

def validate_token(token_in, filename):
    if KEY is None:
        return
    if not token_in:
        raise Exception("Auth token is missing.")
    if ':' not in token_in:
        raise Exception("Auth token is malformed.")
    mac_in, timestr = token_in.split(':')
    try:
        timestamp = int(timestr)
    except ValueError:
        raise Exception("Auth token is malformed.")

    if TIME_TOLERANCE is not None:
        current_time = get_timestamp()
        if not abs(current_time - timestamp) < TIME_TOLERANCE:
            raise Exception("Auth token timestamp out of range.")

    expected_token = generate_token(timestamp, filename)
    if token_in != expected_token:
        raise Exception("Auth token is invalid.")

def get_rel_path(coll, thumb_p):
    type_dir = THUMB_DIR if thumb_p else ORIG_DIR
    if COLLECTION_DIRS is None:
        return type_dir
    try:
        coll_dir = COLLECTION_DIRS[coll]
    except KeyError:
        raise Exception(f"Unknown collection: {coll}")
    return os.path.join(coll_dir, type_dir)

def resolve_file(event):
    query = event.get('queryStringParameters', {})
    thumb_p = (query.get('type') == 'T')
    storename = query.get('filename')
    coll = query.get('coll')
    relpath = get_rel_path(coll, thumb_p)
    return os.path.join(relpath, storename)