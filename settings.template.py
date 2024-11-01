import os

# Sample Specify web asset server settings.

# Turns on bottle.py debugging, module reloading and printing some
# information to console.
LOG_LEVEL = "INFO"

DEBUG_APP = True

# This secret key is used to generate authentication tokens for requests.
# The same key must be set in the Web Store Attachment Preferences in Specify.
# A good source for key value is: https://www.grc.com/passwords.htm
# Set KEY to None to disable security. This is NOT recommended since doing so
# will allow anyone on the internet to use the attachment server to store
# arbitrary files.
KEY = 'redacted'

# Auth token timestamp must be within this many seconds of server time
# in order to be considered valid. This prevents replay attacks.
# Set to None to disable time validation.
TIME_TOLERANCE = 150

# Set this to True to require authentication for downloads in addition
# to uploads and deletes.  Static file access, if enabled, is not
# affected by this setting.
REQUIRE_KEY_FOR_GET = False

# This is required for use with the Web Portal.
# Enables the 'getfileref' and '/static/...' URLs.
ALLOW_STATIC_FILE_ACCESS = True

# These values are interpolated into the web_asset_store.xml resource
# so the client knows how to talk to the server.
# HOST = '192.168.1.224'

# Image server host and port info
if "EXTERNAL_IP" in os.environ:
    HOST = os.getenv('EXTERNAL_IP')
    # print(f"Got external Ip from environment:{HOST}")
else:
    import socket


    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    HOST = local_ip
    # print(f"Got external Ip from gethostbyname:{HOST}")

# use this server name if on backend
# HOST = 'http://instutution.org'
PORT = 80
SERVER_NAME = f"{HOST}"
SERVER_PORT = PORT
SERVER_PROTOCOL = "https"
print(f"Starting with host: {HOST}")
DEVELOPMENT_PORT = PORT

# set to TRUE when using port other than 80 on http or 443 on https, as requests defaults to 80/443 in the url
OVERRIDE_PORT = False

# default text encoding for command line level subprocesses.
ENCODING = "C.UTF-8"

# Map collection names to directories.  Set to None to store
# everything in the same originals and thumbnail directories.  This is
# recommended unless some provision is made to allow attachments for
# items scoped above collections to be found.

COLLECTION_DIRS = {
    # 'COLLECTION_NAME': 'DIRECTORY_NAME',
    'Botany': 'botany',
    'Ichthyology': 'ichthyology',
}

# Base directory for all attachments.
BASE_DIR = './attachments/'

# Originals and thumbnails are stored in separate directories.
THUMB_DIR = 'thumbnails'
ORIG_DIR = 'originals'

# Set of mime types that the server will try to thumbnail.
CAN_THUMBNAIL = {'image/jpeg', 'image/gif', 'image/png', 'image/tiff', 'application/pdf'}

# What HTTP server to use for stand-alone operation.
# SERVER = 'paste' # Requires python-paste package. Fast, and seems to work good.
SERVER = 'wsgiref'  # For testing. Requires no extra packages.

#Image databse connection information
SQL_USER='redacted'
SQL_PASSWORD='redacted'
SQL_HOST='http://instutution.org'
SQL_PORT=3306
SQL_DATABASE='images'
