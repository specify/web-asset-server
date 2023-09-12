#!/usr/bin/env python3
#  this was a one-off chuck of code; its purpose was to
# convert already imported images (with a local windows drive location) to cloud hosted.
# retained in archive in case we ever need something like this again.
# 5/4/22 Joe R.

from db_utils import DbUtils, InvalidFilenameError, DatabaseInconsistentError
import ich_importer_config
from attachment_utils import AttachmentUtils

class UploadFailureException(Exception):
    pass

import logging
import os
import filetype
import sys
from imageclient import ImageClient


specify_db_connection = None
attachment_utils = None
image_client = None


COLLECTION = 'Ichthyology'




def process_attachment_record(attachment_record):
    # print(f"record: {attachment_record}")
    attachment_id = attachment_record[0]
    windows_path = attachment_record[1]
    original_path = windows_path
#     record: (983, 'N:\\ichthyology\\images\\CAS other\\Expedition Images Linked to Specify\\Philippines-2016\\Jeffs-Photos\\JTW-photos_L21-7082\\Macropharygnodon meleagris_43 mm SL_PHISH-091_PHISH-2016-13_MAB-308_Photo by JTWilliams_2016-04-14 16-04-50.jpg')
#     /Volumes/data/ichthyology/
    linux_path = windows_path.replace('\\','/')
    linux_path = linux_path.replace("N:/","/Volumes/data/")
    # print(f"  fixed: {windows_path}")
    exists= os.path.exists(linux_path)
    if exists:
        # print(f"   Found!")
        pass
    else:
        print(f"   Not found - attachment record ID: {attachment_id}: \n\tAttempted path:{linux_path}\n\tOriginal path:{original_path}")
        return

    if image_client.check_image_db_if_already_imported(COLLECTION,os.path.basename(linux_path)):
        print(f"Image {windows_path} already updated, skipping..", file=sys.stderr, flush=True)
        return
    # joe:
    # get collection object ID from attachment
    sql = f"Select CollectionObjectID from collectionobjectattachment where AttachmentID = {attachment_id}"
    # check

    collection_object_id = specify_db_connection.get_one_record(sql)
    if collection_object_id is None:
        print(f"No collection object? {sql}")
        return

    is_redacted = attachment_utils.get_is_collection_object_redacted(collection_object_id)
    logging.debug(f" Collection object id: {collection_object_id} with attachment id: {attachment_id} and path {windows_path}. Redacted: {is_redacted}")
    try:
        url,location = image_client.upload_to_image_server(linux_path, is_redacted, COLLECTION)
        update_attachment_record(attachment_id,linux_path, url, location)


    except UploadFailureException:
        logging.error(f"Upload failure to image server for file: {linux_path}")
    return

def update_attachment_record(attachment_record_id,linux_path,url, location):
    sql = f"update attachment  set origFilename='{linux_path}', Remarks='{url}', AttachmentLocation='{location}' where AttachmentID={attachment_record_id}"
    print(f"sql: {sql}")
    specify_db_connection.execute(sql)

def iterate_existing_attachments():
    global specify_db_connection, attachment_utils, image_client

    specify_db_connection = DbUtils(
        ich_importer_config.USER,
        ich_importer_config.PASSWORD,
        ich_importer_config.SPECIFY_DATABASE_PORT,
        ich_importer_config.SPECIFY_DATABASE_HOST,
        ich_importer_config.SPECIFY_DATABASE)
    attachment_utils = AttachmentUtils(specify_db_connection)
    image_client = ImageClient()

    sql = f"select AttachmentID,origFilename from attachment where AttachmentLocation is not NULL"
    cursor = specify_db_connection.get_cursor()
    cursor.execute(sql)
    attachment_records = cursor.fetchall()
    cursor.close()
    for attachment_record in attachment_records:
        process_attachment_record(attachment_record)


def main():
    logging.basicConfig(level=logging.ERROR)

    iterate_existing_attachments()



if __name__ == '__main__':
    main()