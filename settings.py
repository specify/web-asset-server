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

# Map collection names to directories.  Set to None to store
# everything in the same originals and thumbnail directories.  This is
# recommended unless some provision is made to allow attachments for
# items scoped above collections to be found.
COLLECTION_S3_PATHS = {
    'coll1': 's3://my-bucket/path/to/coll1',
    'coll2': 's3://my-bucket/path/to/coll2',
    # ... add all your collections here ...
}

# Local BASE_DIR no longer used for attachments; kept for static assets
BASE_DIR = '/home/specify/attachments'

THUMB_DIR = 'thumbnails'
ORIG_DIR = 'originals'
CAN_THUMBNAIL = {
    'image/jpeg','image/gif','image/png',
    'image/tiff','application/pdf'
}

# What HTTP server to use for stand-alone operation.
# SERVER = 'paste' # Requires python-paste package. Fast, and seems to work good.
# use wsgiref for testing. Requires no extra packages.
SERVER = 'paste'  # or 'wsgiref'
