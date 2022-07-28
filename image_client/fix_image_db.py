#!/usr/bin/env python
# synchronizes from specify to the image database to fix an import error.
# keeping in case we ever get image DB corruption again...
import ich_importer_config
from image_db import ImageDb
import os.path
from datetime import datetime


from db_utils import DbUtils, InvalidFilenameError, DatabaseInconsistentError

specify_db_connection = DbUtils(
    ich_importer_config.USER,
    ich_importer_config.PASSWORD,
    ich_importer_config.SPECIFY_DATABASE_PORT,
    ich_importer_config.SPECIFY_DATABASE_HOST,
    ich_importer_config.SPECIFY_DATABASE)
image_db = ImageDb()

sql = "select AttachmentLocation, origFilename, Remarks from attachment"
# AttachmentLocation 678ac142-0d6f-4d25-ae42-51939aaf41f3.JPG
# origFilename /Volumes/data/ichthyology/images/CAS other/Expedition Images Linked to Specify/Philippines-2014/DC-1649c.JPG
# Remarks http://ibss-images.calacademy.org:80/static/ichthyology/originals/4c/49/4c498a67-c484-40fb-96d9-925684dd4c72.JPG
cursor = specify_db_connection.get_cursor()
cursor.execute(sql)
attachment_records = cursor.fetchall()
cursor.close()
specify_db_connection.connect()
goodcount = badcount = 0
for attachment_record in attachment_records:
    url = attachment_record[2]
    original_path = attachment_record[1]
    original_path = original_path.replace('\\','/')
    original_path = original_path.replace("N:/","/Volumes/data/")

    internal_filename = attachment_record[0]
    original_filename = os.path.basename(original_path)
    sql = f"select count(*) from images where internal_filename = '{internal_filename}'"
    # sql = f"select count(*) from images"

    # print(f"Checking  '{attachment_record[0]}' : {sql}")
    image_cursor = image_db.get_cursor()
    image_cursor.execute(sql)
    retval = int(image_cursor.fetchone()[0])
    image_cursor.close()

    if retval == 0:
        badcount += 1
        datetime_now = datetime.utcnow()

        if not internal_filename.startswith('sp6'):
            image_db.create_image_record(original_filename,url,internal_filename, 'Ichthyology',original_path,"",False, datetime.utcnow())
            # sql = (f'''
            # insert into images (original_filename,url,images.images.internal_filename, 'Ichthyology',original_path,"",False, datetime.utcnow())
            #
            # # original_path, internal_filename, url, redacted,collection,datetime) values
            # ('{original_filename}','{original_path}','{internal_filename}','{url}',False,'Ichthyology',"{datetime_record.strftime(TIME_FORMAT_NO_OFFESET)}")  ''')
            # # image_db.execute(sql)
            # print(f"sql: {sql}")
    else:
        goodcount +=1
        # print(f"Good retval:{retval} sql: {sql}")


print(f"Good: {goodcount} bad: {badcount}")
