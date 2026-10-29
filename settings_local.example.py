# Copy to settings_local.py and customize for your institution!
HOST = 'assets.example.edu'  # Asset server hostname
KEY = 'replace-with-your-own-secret'  # Must match the one configured in the Specify environment 

# Map collection names to directories.  Set to None to store
# everything in the same originals and thumbnail directories.  This is
# recommended unless some provision is made to allow attachments for
# items scoped above collections to be found.
COLLECTION_S3_PATHS = {
    'Example Collection': 's3://your-bucket/your-prefix',
}

# Optional overrides:
# PORT = 8080
# SERVER_NAME = HOST
# DEBUG = False