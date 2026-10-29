import os

# Sample Specify web asset server settings.

# Bottle / server settings
# Turns on bottle.py debugging, module reloading and printing some
# information to console.
DEBUG = False
#DEBUG = True

# This secret key is used to generate authentication tokens for requests.
# The same key must be set in the Web Store Attachment Preferences in Specify.
# A good source for key value is: https://www.grc.com/passwords.htm
# Set KEY to None to disable security. This is NOT recommended since doing so
# will allow anyone on the internet to use the attachment server to store
# arbitrary files.
KEY = 'test_attachment_key'
TIME_TOLERANCE = 600
REQUIRE_KEY_FOR_GET = False

# This is required for use with the Web Portal.
# Enables the 'getfileref' and '/static/...' URLs.
ALLOW_STATIC_FILE_ACCESS = True

# These values are interpolated into the web_asset_store.xml resource
# so the client knows how to talk to the server.
HOST = 'localhost'
PORT = 8080
SERVER_NAME = HOST
SERVER_PORT = PORT
DEVELOPMENT_PORT = PORT # Port the development test server should listen on.

# Institution-specific S3 mappings belong in settings_local.py.
COLLECTION_S3_PATHS = {}
STORAGE_BACKEND = 'local'  # Set to 's3' explicitly to use object storage.
COLLECTION_DIRS = None  # Local: shared root, or {collection: relative directory}.

# Root directory for local attachments.
BASE_DIR = '/home/specify/attachments'

THUMB_DIR = 'thumbnails'
ORIG_DIR = 'originals'
# Set of mime types that the server will try to thumbnail.
CAN_THUMBNAIL = {
    'image/jpeg', 'image/gif', 'image/png', 'image/tiff',
    'application/pdf', 'image/heic', 'image/heif',
}

# What HTTP server to use for stand-alone operation.
# SERVER = 'paste' # Requires python-paste package. Fast, and seems to work good.
# use wsgiref for testing. Requires no extra packages.
SERVER = 'paste'  # or 'wsgiref'

ALT_DIR = None

ALT_DIR_COLLECTIONS = {}

# Institution-specific overrides; see CONFIGURATION.md.
try:
    import settings_local as _local_settings
except ModuleNotFoundError as exc:
    if exc.name != 'settings_local':
        raise
else:
    for _name in dir(_local_settings):
        if _name.isupper() and not _name.startswith('_'):
            globals()[_name] = getattr(_local_settings, _name)
    # Derive these after overrides unless the institution explicitly sets them.
    SERVER_NAME = getattr(_local_settings, 'SERVER_NAME', HOST)
    SERVER_PORT = getattr(_local_settings, 'SERVER_PORT', PORT)
    DEVELOPMENT_PORT = getattr(_local_settings, 'DEVELOPMENT_PORT', PORT)
