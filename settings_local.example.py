# Copy to settings_local.py and customize for your institution.
HOST = 'assets.example.edu'
KEY = 'replace-with-your-own-secret'  # Must match Specify attachment preferences.

# Local storage is the default.
STORAGE_BACKEND = 'local'
BASE_DIR = '/home/specify/attachments'
COLLECTION_DIRS = None  # Collections share originals/ and thumbnails/.
# Or isolate collections under the base directory:
# COLLECTION_DIRS = {'Example Collection': 'example'}

# Optional: use S3 instead of local storage.
# STORAGE_BACKEND = 's3'
# COLLECTION_S3_PATHS = {
#     'Example Collection': 's3://your-bucket/your-prefix',
# }

# PORT = 8080
# SERVER_NAME = HOST
# SERVER_PORT = 443
# DEBUG = False
