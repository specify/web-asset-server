import os
import ast

# Sample Specify web asset server settings.

# Turns on bottle.py debugging, module reloading and printing some
# information to console.
DEBUG = (os.environ.get('DEBUG') or os.environ.get('DEBUG_MODE', 'True')).lower() == 'true'

# This secret key is used to generate authentication tokens for requests.
# The same key must be set in the Web Store Attachment Preferences in Specify.
# A good source for key value is: https://www.grc.com/passwords.htm
# Set KEY to None to disable security. This is NOT recommended since doing so
# will allow anyone on the internet to use the attachment server to store
# arbitrary files.
KEY = os.environ.get('KEY') or os.environ.get('ATTACHMENT_KEY') or 'test_attachment_key'

# Auth token timestamp must be within this many seconds of server time
# in order to be considered valid. This prevents replay attacks.
# Set to None to disable time validation.
TIME_TOLERANCE = int(os.environ.get('TIME_TOLERANCE', '150'))

# Set this to True to require authentication for downloads in addition
# to uploads and deletes.  Static file access, if enabled, is not
# affected by this setting.
REQUIRE_KEY_FOR_GET = os.environ.get('REQUIRE_KEY_FOR_GET', 'False').lower() == 'true'

# This is required for use with the Web Portal.
# Enables the 'getfileref' and '/static/...' URLs.
ALLOW_STATIC_FILE_ACCESS = os.environ.get('ALLOW_STATIC_FILE_ACCESS', 'True').lower() == 'true'

# These values are interpolated into the web_asset_store.xml resource
# so the client knows how to talk to the server.
HOST = os.environ.get('HOST') or os.environ.get('SERVER_NAME') or 'localhost'
PORT = int(os.environ.get('PORT') or os.environ.get('SERVER_PORT') or '8080')

SERVER_NAME = HOST
SERVER_PORT = PORT

# Port the development test server should listen on.
DEVELOPMENT_PORT = PORT

# Map collection names to directories.  Set to None to store
# everything in the same originals and thumbnail directories.  This is
# recommended unless some provision is made to allow attachments for
# items scoped above collections to be found.

# COLLECTION_DIRS = {
#     # 'COLLECTION_NAME': 'DIRECTORY_NAME',
#     'KUFishvoucher': 'Ichthyology',
#     'KUFishtissue': 'Ichthyology',
# }

COLLECTION_DIRS = ast.literal_eval(os.environ.get('COLLECTION_DIRS', '{}'))

# Base directory for all attachments.
BASE_DIR = os.environ.get('BASE_DIR', '/home/specify/attachments/')

# Originals and thumbnails are stored in separate directories.
THUMB_DIR = os.environ.get('THUMB_DIR', 'thumbnails')
ORIG_DIR = os.environ.get('ORIG_DIR', 'originals')

# Set of mime types that the server will try to thumbnail.
CAN_THUMBNAIL = {'image/jpeg', 'image/gif', 'image/png', 'image/tiff', 'application/pdf'}

# What HTTP server to use for stand-alone operation.
# SERVER = 'paste' # Requires python-paste package. Fast, and seems to work good.
# SERVER = 'wsgiref'  # For testing. Requires no extra packages.
SERVER = os.environ.get('SERVER', 'wsgiref')

