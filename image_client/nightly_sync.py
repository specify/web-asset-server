from image_db import ImageDb
from attachment_utils import AttachmentUtils
from db_utils import DbUtils
import botany_importer_config
import ich_importer_config

import logging
from time import sleep
import sys

image_db = None
botany_importer = None
attachment_utils = None


def get_specify_state(internal_filename):
    global attachment_utils
    coid = attachment_utils.get_collectionobjectid_from_filename(internal_filename)
    if coid is None:
        return None
    redacted_collection_object = attachment_utils.get_is_collection_object_redacted(coid)
    redacted_attachment = attachment_utils.get_is_attachment_redacted(internal_filename)
    logging.debug(
        f"get specify state {internal_filename}, colleciton object: {coid} collection object state: {redacted_collection_object} attachment state: {redacted_attachment}")

    return redacted_collection_object or redacted_attachment


def redact(internal_filename, redacted):
    logging.debug("\n\n----------")
    logging.debug(f"Checking: {internal_filename} currently {redacted}")
    redacted_in_specify = get_specify_state(internal_filename)
    if redacted_in_specify is None:
        logging.warning(f"Cannot find collection object ID for {internal_filename}")
    elif redacted_in_specify != redacted:
        logging.debug(f"State change!")
        image_db.update_redacted(internal_filename, redacted_in_specify)
    else:
        logging.debug(f"No state change required. State is {redacted} object is {internal_filename}")


def do_import(collection_name,specify_db_connection):
    global image_db, attachment_utils

    print(f"Starting sync..")
    image_db = ImageDb()
    attachment_utils = AttachmentUtils(specify_db_connection)
    cursor = image_db.get_cursor()
    query = f"""SELECT  internal_filename,  redacted FROM images where collection='{collection_name}'"""

    cursor.execute(query)
    record_list = []
    found_tuples = []
    for (internal_filename, redacted) in cursor:
        found_tuples.append((internal_filename, redacted))
    cursor.close()
    for (internal_filename, redacted) in found_tuples:
        next_record = False
        while next_record is False:
            try:
                redact(internal_filename, redacted)
                next_record = True
            except ReferenceError as e:
                print(f"Reference error, skipping: {e}", file=sys.stderr, flush=True)
                print(f"   internal filename: {internal_filename} redacted: {redacted}", file=sys.stderr, flush=True)
                next_record = True
            except Exception as e:
                print(f"Error, probably sql {e}", file=sys.stderr, flush=True)
                print(f"exception type: {type(e).__name__}", file=sys.stderr, flush=True)


    return record_list

def main():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    if len(sys.argv) != 2:
        print("Need a collection argument.")
        sys.exit(1)
    if sys.argv[1] == "Botany":
        collection_name = botany_importer_config.COLLECTION_NAME
        specify_db_connection = DbUtils(
            botany_importer_config.USER,
            botany_importer_config.PASSWORD,
            botany_importer_config.SPECIFY_DATABASE_PORT,
            botany_importer_config.SPECIFY_DATABASE_HOST,
            botany_importer_config.SPECIFY_DATABASE)
    elif sys.argv[1] == "Ichthyology":
        collection_name = ich_importer_config.COLLECTION_NAME
        specify_db_connection = DbUtils(
            ich_importer_config.USER,
            ich_importer_config.PASSWORD,
            ich_importer_config.SPECIFY_DATABASE_PORT,
            ich_importer_config.SPECIFY_DATABASE_HOST,
            ich_importer_config.SPECIFY_DATABASE)
    do_import(collection_name,specify_db_connection)


if __name__ == '__main__':
    main()


