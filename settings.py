DEBUG = True

# These values are interpolated into the web_asset_store.xml resource so the client
# knows how to talk to the server.
HOST = 'dhwd99p1.nhm.ku.edu'
PORT = 3088

# Port the development test server should listen on.
DEVELOPMENT_PORT = 3088

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
