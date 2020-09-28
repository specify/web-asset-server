import settings
import boto3
import sys
import commons
import json
from os import path
from tempfile import NamedTemporaryFile
from collections import defaultdict
from time import time

print('Warning! This script is only supposed to work with files that are already in a digitalocean bucket\n' +
      'If you have local files, please run `transfer.py` first\n')


def validate_settings():
    try:
        if settings.STORAGE_TYPE != 'digitalocean_spaces':
            print('settings.STORAGE_TYPE is not set to `digitalocean_spaces`. Don\'t forget to change that!')

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


# Validating settings before proceeding
assert validate_settings()

# Connecting to the bucket
session = boto3.session.Session()
client = session.client('s3',
                        region_name=settings.DIGITALOCEAN_REGION,
                        endpoint_url='https://%s.digitaloceanspaces.com' % settings.DIGITALOCEAN_REGION,
                        aws_access_key_id=settings.DIGITALOCEAN_KEY,
                        aws_secret_access_key=settings.DIGITALOCEAN_SECRET)

# Checking if chosen bucket exists
response = client.list_buckets()
buckets = {bucket['Name'] for bucket in response['Buckets']}

# Creating new bucket if needed
if settings.DIGITALOCEAN_SPACE_NAME not in buckets:
    print('Bucket %s does not exist' % settings.DIGITALOCEAN_SPACE_NAME)
    sys.exit(0)

# Downloading files
print("Downloading list of files")

objects = defaultdict(list)
last_key = ''
while True:
    response = client.list_object_versions(Bucket=settings.DIGITALOCEAN_SPACE_NAME,
                                           KeyMarker=last_key)

    if 'Versions' not in response and last_key == '':
        print('No files were found in the digitalocean space. Make sure you run `transfer.py` beforehand')
        sys.exit(0)

    {objects[item['ETag']].append(item['Key']) for item in response['Versions'] if item['Size'] != 0}
    if response['IsTruncated']:
        last_key = response['Version'][-1]['Key']
    else:
        break

# Filtering out non unique files
objects = dict(objects)
objects = {file_hash: files for file_hash, files in objects.items() if len(files) > 1}

number_of_unique_files = len(objects.keys())
number_of_non_unique_files = len([file for files in objects.values() for file in files])

if number_of_unique_files == 0:
    print('There were no duplicate files found')
    sys.exit(0)

print('The following duplicate files were found: \n'
      '%s\n'
      'As a result, %d files would be reduced to %d files' % (
          '\n'.join([' '.join(files) for files in objects.values()]),
          number_of_non_unique_files,
          number_of_unique_files
      ))

# Confirming before starting
commons.confirm_action('Do you want to continue?')

# Uploading files one by one (no bulk upload option available)
start_time = time()
current_file = 1
current_position = 1

for file_hash, files in objects.items():

    try:
        first_file_name = files[0]
    except IndexError:
        continue

    metadata = commons.digitalocean_get_file(client=client,
                                             file_name=first_file_name,
                                             return_type='meta')

    metadata['references'] = json.dumps(files)  # saving the list of references to this file

    print('[%d/%d] Uploading deduplicated file' % (current_file, number_of_unique_files))

    client.copy_object(Bucket=settings.DIGITALOCEAN_SPACE_NAME,
                       Key=file_hash,
                       CopySource={
                           'Bucket': settings.DIGITALOCEAN_SPACE_NAME,
                           'Key': first_file_name,
                       },
                       Metadata=metadata)

    duplicate_object_metadata = {
                                  'redirect': file_hash
                              }

    for file_name in files:
        print('[%d/%d] Creating links from duplicates to target files' %
              (current_position, number_of_non_unique_files)
              )
        client.put_object(Bucket=settings.DIGITALOCEAN_SPACE_NAME,
                          Key=file_name,
                          Body='',
                          ACL='private',
                          Metadata=duplicate_object_metadata)

        current_position = current_position + 1

    current_file = current_file + 1

end_time = time()

print('Deduplication finished in %.2f seconds' % (end_time - start_time))
