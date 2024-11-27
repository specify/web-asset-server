# assets_settings.py

# Settings (adjust these as needed)
DEBUG = True
KEY = ''  # Replace with your actual key
TIME_TOLERANCE = 150
REQUIRE_KEY_FOR_GET = True
BASE_DIR = '/mnt/efs'  # EFS mount point in Lambda
THUMB_DIR = 'thumbnails'
ORIG_DIR = 'originals'
CAN_THUMBNAIL = {'image/jpeg', 'image/gif', 'image/png', 'image/tiff', 'application/pdf'}
COLLECTION_DIRS = None

################################################################################

# Sample Specify web asset server settings.

# Turns on bottle.py debugging, module reloading and printing some
# information to console.
DEBUG = False

# This secret key is used to generate authentication tokens for requests.
# The same key must be set in the Web Store Attachment Preferences in Specify.
# A good source for key value is: https://www.grc.com/passwords.htm
# Set KEY to None to disable security. This is NOT recommended since doing so
# will allow anyone on the internet to use the attachment server to store
# arbitrary files.
KEY = ''

# Auth token timestamp must be within this many seconds of server time
# in order to be considered valid. This prevents replay attacks.
# Set to None to disable time validation.
TIME_TOLERANCE = 600

# Set this to True to require authentication for downloads in addition
# to uploads and deletes.  Static file access, if enabled, is not
# affected by this setting.
REQUIRE_KEY_FOR_GET = False

# This is required for use with the Web Portal.
# Enables the 'getfileref' and '/static/...' URLs.
ALLOW_STATIC_FILE_ACCESS = True

# Map collection names to directories.  Set to None to store
# everything in the same originals and thumbnail directories.  This is
# recommended unless some provision is made to allow attachments for
# items scoped above collections to be found.

# COLLECTION_DIRS = {
#     # 'COLLECTION_NAME': 'DIRECTORY_NAME',
#     'KUFishvoucher': 'Ichthyology',
#     'KUFishtissue': 'Ichthyology',
# }

# Base directory for all attachments.
BASE_DIR = '/home/specify/attachments'

# Originals and thumbnails are stored in separate directories.
THUMB_DIR = 'thumbnails'
ORIG_DIR = 'originals'

# Set of mime types that the server will try to thumbnail.
CAN_THUMBNAIL = {'image/jpeg', 'image/gif', 'image/png', 'image/tiff', 'application/pdf'}
