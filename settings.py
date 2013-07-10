DEBUG = True

# This secret key is used to generate authentication tokens for requests.
# The same key must be set in the Web Store Attachment Preferences in Specify.
# A good source for key value is: https://www.grc.com/passwords.htm
# Set KEY to None to disable security. This is NOT recommended since doing so
# will allow anyone on the internet to use the attachment server to store
# arbitrary files.
KEY = 'test_attachment_key'

# Auth token timestamp must be within this many seconds of server time
# in order to be considered valid. This prevents replay attacks.
# Set to None to disable time validation.
TIME_TOLERANCE = 150

# Set this to False to only require authentication for uploads and deletes.
# Static file access, if enabled, is not affected by this setting.
REQUIRE_KEY_FOR_GET = True

# This is required for use with the Web Portal.
ALLOW_STATIC_FILE_ACCESS = True

# These values are interpolated into the web_asset_store.xml resource so the client
# knows how to talk to the server.
HOST = 'dhwd99p1.nhm.ku.edu'
PORT = 3080

# Port the development test server should listen on.
DEVELOPMENT_PORT = PORT

# Map collection names to directories.
COLLECTION_DIRS = {
    # 'COLLECTION_NAME': 'DIRECTORY_NAME',
    'KUFishvoucher': 'Ichthyology',
    'KUFishtissue': 'Ichthyology',
}

# Base directory for all attachments.
BASE_DIR = '/home/ben/attachments/'

# Originals and thumbnails are stored in separate directories.
THUMB_DIR = 'thumbnails'
ORIG_DIR = 'originals'

# Set of mime type that the server will try to thumbnail.
CAN_THUMBNAIL = {'image/jpeg', 'image/gif', 'image/png', 'image/tiff', 'application/pdf'}

# What HTTP server to use for stand-alone operation.
# SERVER = 'cherrypy' # Cherrypy is faster but less debugging output.
SERVER = 'wsgiref'  # For testing.
