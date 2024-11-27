# lambda_function.py

import logging
from assets_file_handlers import fileget, fileupload, filedelete, getmetadata, testkey, generate_xml
from assets_settings import DEBUG

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    path = event.get('rawPath', event.get('path', ''))
    method = event['httpMethod']
    headers = event.get('headers', {})
    protocol = 'https' if headers.get('x-forwarded-proto') == 'https' else 'http'
    host = headers.get('host', 'localhost')
    base_url = f"{protocol}://{host}"

    if DEBUG:
        logger.info(f"Received {method} request for {path}")

    # Map paths and methods to functions
    if path == '/fileget' and method == 'GET':
        return fileget(event)
    elif path == '/fileupload' and method == 'POST':
        return fileupload(event)
    elif path == '/filedelete' and method == 'POST':
        return filedelete(event)
    elif path == '/getmetadata' and method == 'GET':
        return getmetadata(event)
    elif path == '/testkey' and method == 'GET':
        return testkey(event)
    elif path == '/web_asset_store.xml' and method == 'GET':
        xml_body = generate_xml(base_url)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/xml'
            },
            'body': xml_body
        }
    else:
        return {
            'statusCode': 404,
            'body': 'Not Found'
        }