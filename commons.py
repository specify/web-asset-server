import sys
import settings
import boto3
import botocore


def confirm_action(action):
    choice = ' '
    while choice != 'y' and choice != '':
        if choice in 'n':
            print('Abort')
            sys.exit(0)
        else:
            print(action + ' [Y/n]')
        choice = input().lower()


def connect():
    session = boto3.session.Session()
    client = session.client('s3',
                            region_name=settings.DIGITALOCEAN_REGION,
                            endpoint_url='https://%s.digitaloceanspaces.com' % settings.DIGITALOCEAN_REGION,
                            aws_access_key_id=settings.DIGITALOCEAN_KEY,
                            aws_secret_access_key=settings.DIGITALOCEAN_SECRET)

    return client
