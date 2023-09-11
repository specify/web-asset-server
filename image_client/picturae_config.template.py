import os
SPECIFY_DATABASE_HOST = 'db-institution.name'
SPECIFY_DATABASE_PORT = 3306
SPECIFY_DATABASE = 'redacted'
USER = 'redacted'
PASSWORD = 'redacted'

PIC_REGEX = '(CAS|cas)[0-9]*([\-_])*[0-9a-zA-Z]?.(JPG|jpg|jpeg|TIFF|tif)'

sla = os.path.sep
# config paths files
date_str = None

PIC_PREFIX = f'picturae_img{sla}'
PIC_SCAN_FOLDERS = [f'PIC_{date_str}']
PREFIX = f"web-asset-server{sla}image_client{sla}"

# number for created by agent field , check your agent id on the agent table
agent_number = 123456