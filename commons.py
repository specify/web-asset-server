import sys
import settings
import boto3
import botocore


"""
Span a prompt asking user to confirm a certain action
@param {str} confirmation_message - The message that would be shown to the user
"""
def confirm_action(confirmation_message: str):
    choice = ' '
    while choice != 'y' and choice != '':
        if choice in 'n':
            print('Abort')
            sys.exit(0)
        else:
            print(confirmation_message + ' [Y/n]')
        choice = input().lower()


"""
Connect to a digitalocean's space
"""
def connect():
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name=settings.DIGITALOCEAN_REGION,
                            endpoint_url='https://%s.digitaloceanspaces.com' % settings.DIGITALOCEAN_REGION,
                            aws_access_key_id=settings.DIGITALOCEAN_KEY,
                            aws_secret_access_key=settings.DIGITALOCEAN_SECRET)

    return client


"""
A multipurpose object that can tell whether a file exists and return it's metadata or content
@param {object} client - a pointer to a connection client (returned by commons.connect())
@param {str} file_name - a file key as stored in the digitalocean's space
@param {str} return_type - a type of data to be requested from the server
                           if return_type is 'meta', then returns file's metadata. Returns {} if file does not exist
                           if return_type is 'file', writes file content into `file_object`. Returns whether file exists
                           if return_type is 'file_exists', returns whether file exists
@param {mixed} - if return_type is 'file' - {TextIOWrapper} a file object to write result to
@param {bool} follow_redirect - whether to follow redirects to source file
@returns if return_type is 'meta' - {Set} file_exists, file_metadata
                if file_exists, then file_metadata is file's metadata
                else, file_metadata = {}
         if return_type is 'file' - {bool} file exists if
"""
def digitalocean_get_file(client,
                          file_name: str,
                          return_type: str = 'meta',
                          file_object=None,
                          follow_redirect: bool = True):
    try:

        meta = client.head_object(Bucket=settings.DIGITALOCEAN_SPACE_NAME, Key=file_name)['Metadata']

        if 'redirect' in meta and follow_redirect:
            file_name = meta['redirect']
            meta = client.head_object(Bucket=settings.DIGITALOCEAN_SPACE_NAME, Key=file_name)['Metadata']

        if return_type == 'meta':
            return True, meta
        elif return_type == 'file_exists':
            return True
        elif return_type == 'file':
            client.download_fileobj(settings.DIGITALOCEAN_SPACE_NAME, file_name, file_object)
            file_object.seek(0)
            return True
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            if return_type == 'meta':
                return False, {}
            elif return_type == 'file_exists':
                return False
            elif return_type == 'file':
                return False
        else:
            raise
