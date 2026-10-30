import os

# Sample Specify web asset server settings.

# Bottle / server settings
# Turns on bottle.py debugging, module reloading and printing some
# information to console.
DEBUG = False
LOG_LEVEL = 'INFO'
METADATA_CONCURRENCY = 1
METADATA_MAX_BYTES = 32 * 1024 * 1024
METADATA_MEMORY_BYTES = 192 * 1024 * 1024
METADATA_TIMEOUT_SECONDS = 10
# Per server process; cached thumbnails and original reads bypass this limit.
THUMBNAIL_CONCURRENCY = 1
THUMBNAIL_QUEUE_SIZE = 5
THUMBNAIL_QUEUE_WAIT_SECONDS = 20
THUMBNAIL_TIMEOUT_SECONDS = 60
THUMBNAIL_MEMORY_LIMIT = '64MiB'
THUMBNAIL_MAP_LIMIT = '64MiB'
THUMBNAIL_DISK_LIMIT = '512MiB'
# Exact proxy peer addresses allowed to supply nginx's overwritten X-Real-IP.
TRUSTED_PROXY_IPS = []
#DEBUG = True

# This secret key is used to generate authentication tokens for requests.
# The same key must be set in the Web Store Attachment Preferences in Specify.
# A good source for key value is: https://www.grc.com/passwords.htm
# Set KEY to None to disable security. This is NOT recommended since doing so
# will allow anyone on the internet to use the attachment server to store
# arbitrary files.
KEY = 'test_attachment_key'
TIME_TOLERANCE = 150
REQUIRE_KEY_FOR_GET = False

# This is required for use with the Web Portal.
# Enables the 'getfileref' and '/static/...' URLs.
ALLOW_STATIC_FILE_ACCESS = True

# These values are interpolated into the web_asset_store.xml resource
# so the client knows how to talk to the server.
HOST = 'localhost'
PORT = 8080
SERVER_NAME = HOST
# Public reverse-proxy port; independent of the internal listener.
SERVER_PORT = 443
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

# 1. Environment overrides shared defaults. 
# 2. Private file overrides environment.
for _name in ('HOST', 'SERVER_NAME', 'STORAGE_BACKEND', 'BASE_DIR', 'LOG_LEVEL'):
    if _name in os.environ:
        globals()[_name] = os.environ[_name]
for _name in ('PORT', 'SERVER_PORT'):
    if _name in os.environ:
        globals()[_name] = int(os.environ[_name])
if 'ATTACHMENT_KEY' in os.environ:
    KEY = os.environ['ATTACHMENT_KEY']
if 'DEBUG_MODE' in os.environ:
    DEBUG = os.environ['DEBUG_MODE'].lower() == 'true'
SERVER_NAME = os.environ.get('SERVER_NAME', HOST)
SERVER_PORT = int(os.environ.get('SERVER_PORT', SERVER_PORT))

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
    SERVER_NAME = getattr(_local_settings, 'SERVER_NAME',
                          HOST if hasattr(_local_settings, 'HOST') else SERVER_NAME)
    SERVER_PORT = getattr(_local_settings, 'SERVER_PORT', SERVER_PORT)
    DEVELOPMENT_PORT = getattr(_local_settings, 'DEVELOPMENT_PORT', PORT)
