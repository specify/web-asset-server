# assets_file_handlers.py

import os
import mimetypes
import logging
import cgi
import io
import urllib.parse
import base64
# from aws_lambda_powertools.utilities.streaming import streamify_response
from assets_utils import (
    validate_token, get_timestamp, resolve_file, get_rel_path
)
from assets_settings import (
    DEBUG, BASE_DIR, THUMB_DIR, ORIG_DIR, COLLECTION_DIRS
)

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# @streamify_response
def fileget(event):
    query = event.get('queryStringParameters', {})
    filename = query.get('filename')
    token = query.get('token')

    # Validate token
    try:
        validate_token(token, filename)
    except Exception as e:
        return {
            'statusCode': 403,
            'body': str(e)
        }

    # Resolve file path
    filepath = resolve_file(event)
    fullpath = os.path.join(BASE_DIR, filepath)
    if not os.path.exists(fullpath):
        return {
            'statusCode': 404,
            'body': 'File not found'
        }

    try:
        content_type, _ = mimetypes.guess_type(fullpath)
        if content_type is None:
            content_type = 'application/octet-stream'

        # Stream the file using aws_lambda_powertools
        with open(fullpath, 'rb') as file_obj:
            headers = {
                'Content-Type': content_type,
                'X-Timestamp': str(get_timestamp())
            }
            return file_obj, headers
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return {
            'statusCode': 500,
            'body': 'Error reading file'
        }
    
def fileupload(event):
    content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
    if not content_type:
        return {
            'statusCode': 400,
            'body': 'Content-Type header is missing'
        }

    try:
        body = event['body']
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body)
        else:
            body = body.encode('utf-8')
        fs = cgi.FieldStorage(
            fp=io.BytesIO(body),
            environ={
                'REQUEST_METHOD': 'POST',
                'CONTENT_TYPE': content_type,
            },
            keep_blank_values=True
        )

        # Get form fields
        type_p = fs.getvalue('type')
        store = fs.getvalue('store')
        coll = fs.getvalue('coll')
        token = fs.getvalue('token')

        # Validate token
        try:
            validate_token(token, store)
        except Exception as e:
            return {
                'statusCode': 403,
                'body': str(e)
            }

        thumb_p = (type_p == 'T')
        basepath = os.path.join(BASE_DIR, get_rel_path(coll, thumb_p))
        pathname = os.path.join(basepath, store)
        if thumb_p:
            return {
                'statusCode': 200,
                'body': 'Ignoring thumbnail upload!'
            }
        if not os.path.exists(basepath):
            os.makedirs(basepath)
        
        # Get the file
        fileitem = fs['file']
        if fileitem.filename:
            with open(pathname, 'wb') as f:
                f.write(fileitem.file.read())
            return {
                'statusCode': 200,
                'body': 'Ok.'
            }
        else:
            return {
                'statusCode': 400,
                'body': 'No file uploaded'
            }
    except Exception as e:
        logger.error(f"Error in file upload: {e}")
        return {
            'statusCode': 500,
            'body': 'Error in file upload'
        }

def filedelete(event):
    content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
    if not content_type:
        return {
            'statusCode': 400,
            'body': 'Content-Type header is missing'
        }

    try:
        body = event['body']
        if event.get('isBase64Encoded'):
            body = base64.b64decode(body).decode('utf-8')
        params = urllib.parse.parse_qs(body)
        filename = params.get('filename', [None])[0]
        coll = params.get('coll', [None])[0]
        token = params.get('token', [None])[0]

        # Validate token
        try:
            validate_token(token, filename)
        except Exception as e:
            return {
                'statusCode': 403,
                'body': str(e)
            }

        # Delete the file
        basepath = os.path.join(BASE_DIR, get_rel_path(coll, thumb_p=False))
        pathname = os.path.join(basepath, filename)
        if os.path.exists(pathname):
            os.remove(pathname)
            return {
                'statusCode': 200,
                'body': 'Ok.'
            }
        else:
            return {
                'statusCode': 404,
                'body': 'File not found'
            }
    except Exception as e:
        logger.error(f"Error in file delete: {e}")
        return {
            'statusCode': 500,
            'body': 'Error in file delete'
        }

def getmetadata(event):
    # Implement EXIF metadata extraction if needed
    return {
        'statusCode': 200,
        'body': 'Metadata feature not implemented.'
    }

def testkey(event):
    # If access to this resource succeeds, clients can conclude
    # that they have a valid access key.
    return {
        'statusCode': 200,
        'body': 'Ok.'
    }

def generate_xml(base_url):
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urls>
    <url type="read">{base_url}/fileget</url>
    <url type="write">{base_url}/fileupload</url>
    <url type="delete">{base_url}/filedelete</url>
    <url type="getmetadata">{base_url}/getmetadata</url>
    <url type="testkey">{base_url}/testkey</url>
</urls>"""
 