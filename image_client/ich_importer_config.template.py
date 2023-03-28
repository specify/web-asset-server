import os
SPECIFY_DATABASE_HOST = 'db.insitution.org'
SPECIFY_DATABASE_PORT = 3306
SPECIFY_DATABASE = 'casich'
USER = 'redacrted'
PASSWORD = 'redacted'
COLLECTION_NAME='Ichthyology'
sla = os.path.sep
# final directory will be prefix + scan dir  and then iterate over all ICH_SCAN_FOLDERS
IMAGE_DIRECTORY_PREFIX = "/letter_drives/n_drive"
SCAN_DIR = f'ichthyology{sla}images{sla}'
ICH_SCAN_FOLDERS = ['AutomaticSpecifyImport']

