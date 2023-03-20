import os
sla = os.path.sep

SPECIFY_DATABASE_HOST = 'db.insitution.org'
SPECIFY_DATABASE_PORT = 3306
SPECIFY_DATABASE = 'casiz'
USER = 'redacrted'
PASSWORD = 'redacted'

IMAGE_DIRECTORY_PREFIX = "/Volumes/data/izg/IZ Images"
COLLECTION_NAME = 'IZ'

MINIMUM_ID_DIGITS = 5
IMAGE_SUFFIX = '[a-z\-\(\)0-9 ©_,.]*(.(jpg|jpeg|tiff|tif|png|PNG))$'
CASIZ_NUMBER = '([0-9]{2,})'
CASIZ_PREFIX = 'cas(iz)?[_ \-]?'
CASIZ_MATCH = CASIZ_PREFIX + CASIZ_NUMBER
FILENAME_MATCH = CASIZ_MATCH + IMAGE_SUFFIX
FILENAME_CONJUNCTION_MATCH = CASIZ_MATCH + f' (and|or) ({CASIZ_PREFIX})?({CASIZ_NUMBER})'


IZ_DIRECTORY_REGEX = CASIZ_MATCH

PREFIX = f"{sla}"


IZ_SCAN_FOLDERS = [
    f'.'
]
# https://exiv2.org/tags.html
EXIF_DECODER_RING = {
    315: 'Artist',
    33432: 'Copyright',
    270: 'ImageDescription'
}
