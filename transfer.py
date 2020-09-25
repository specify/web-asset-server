import settings
import boto3
import botocore
import sys
from os import path
from glob import glob
from pathlib import Path
from server import getmetadata
from time import time


def validate_settings():

    try:
        if settings.STORAGE_TYPE != 'digitalocean_spaces':
            print('settings.STORAGE_TYPE is not set to `digitalocean_spaces`. Don\'t forget to change that!')

        if not path.exists(settings.BASE_DIR):
            raise Exception('Please specify valid settings.BASE_DIR')

        if not settings.DIGITALOCEAN_REGION:
            raise Exception('Please specify valid settings.DIGITALOCEAN_REGION')

        if not settings.DIGITALOCEAN_SPACE_NAME:
            raise Exception('Please specify valid settings.DIGITALOCEAN_SPACE_NAME')

        if not settings.DIGITALOCEAN_KEY:
            raise Exception('Please specify valid settings.DIGITALOCEAN_KEY')

        if not settings.DIGITALOCEAN_SECRET:
            raise Exception('Please specify valid settings.DIGITALOCEAN_SECRET')

    except Exception as e:
        print(e)
        return False

    return True


def confirm_action(action):
    choice = ' '
    while choice != 'y' and choice != '':
        if choice in 'n':
            print('Abort')
            sys.exit(0)
        else:
            print(action + ' [Y/n]')
        choice = input().lower()


# Validating settings before proceeding
assert validate_settings()

print("Searching for files in %s" % settings.BASE_DIR)


# Getting list of all of the files to transfer
files_to_transfer = list(Path(settings.BASE_DIR).rglob("*.*"))

# Ignoring blacklisted files
files_to_ignore = [
    'thumbs.db',
    '.DS_Store',
]

files_to_transfer = [str(file) for file in files_to_transfer if path.basename(str(file)) not in files_to_ignore]

# Removing base path from results
files_to_transfer = [file.replace(settings.BASE_DIR, '') for file in files_to_transfer]

# Displaying the results
[print(file) for file in files_to_transfer]
number_of_results = len(files_to_transfer)
print('%d files would be transferred.' % number_of_results)

# Confirm transfer before starting
confirm_action('Do you want to continue?')

# Connecting to the bucket
session = boto3.session.Session()
client = session.client('s3',
                        region_name=settings.DIGITALOCEAN_REGION,
                        endpoint_url='https://%s.digitaloceanspaces.com' % settings.DIGITALOCEAN_REGION,
                        aws_access_key_id=settings.DIGITALOCEAN_KEY,
                        aws_secret_access_key=settings.DIGITALOCEAN_SECRET)

response = client.list_buckets()
buckets = {bucket['Name'] for bucket in response['Buckets']}

# Creating new bucket if needed
if settings.DIGITALOCEAN_SPACE_NAME not in buckets:
    confirm_action('Bucket %s does not exist. Create bucket?' % settings.DIGITALOCEAN_SPACE_NAME)
    client.create_bucket(Bucket=settings.DIGITALOCEAN_SPACE_NAME)

# Uploading files one by one (no bulk upload option available)
start_time = time()
for file_index, file_name in enumerate(files_to_transfer, start=1):
    print('[%d/%d] Uploading %s' % (file_index, number_of_results, file_name))
    with open(path.join(settings.BASE_DIR, file_name), 'rb') as file_object:
        client.put_object(Bucket=settings.DIGITALOCEAN_SPACE_NAME,
                          Key=file_name,
                          Body=file_object.read(),
                          ACL='private',
                          Metadata={
                              'exif': getmetadata(file_object)
                          })
end_time = time()

print('Upload finished in %.2f seconds' % (end_time - start_time))
