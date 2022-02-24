import botany_importer_config
import mysql.connector
from mysql.connector import errorcode
import logging
import datetime,pytz
from uuid import uuid4
import os
import re

cnx = None


class InvalidFilenameError(Exception):
    pass

class DataInvariantException(Exception):
    pass

def get_pst_time(user_time):
    tz = pytz.timezone('America/Los_Angeles')
    localtime = user_time.astimezone(tz)
    return localtime

def get_pst_time_now():
    datetime_now = datetime.datetime.now(datetime.timezone.utc)
    return get_pst_time(datetime_now)

def get_pst_time_now_string():
    TIME_FORMAT="%Y-%m-%d %H:%M:%S"
    return(get_pst_time_now().strftime(TIME_FORMAT))


def get_pst_date_from_datetime(user_time):
    TIME_FORMAT="%Y-%m-%d"
    return(user_time.strftime(TIME_FORMAT))

def connect():
    global cnx
    if cnx is None:
        logging.debug("Connecting to db...")

        try:
            cnx = mysql.connector.connect(user=botany_importer_config.USER,
                                          password=botany_importer_config.PASSWORD,
                                          host=botany_importer_config.SPECIFY_DATABASE_HOST,
                                          port=botany_importer_config.SPECIFY_DATABASE_PORT,
                                          database=botany_importer_config.SPECIFY_DATABASE)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.error(f"Starting client...")

                logging.error("SQL: Access denied")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.error("Database does not exist")
            else:
                logging.error(err)

        logging.info("Db connected")
    else:
        logging.debug("Already connected.")

def create_attachment(storename,original_filename,file_created_datetime,guid,image_type,url):
    # image type example 'image/png'

    sql = (f"""
            INSERT INTO `attachment` (`attachmentlocation`, `attachmentstorageconfig`, `capturedevice`, `copyrightdate`,
                                      `copyrightholder`, `credit`, `dateimaged`, `filecreateddate`, `guid`, `ispublic`, `license`,
                                      `licenselogourl`, `metadatatext`, `mimetype`, `origfilename`, `remarks`, `scopeid`,
                                      `scopetype`, `subjectorientation`, `subtype`, `tableid`, `timestampcreated`,
                                      `timestampmodified`, `title`, `type`, `version`, `visibility`, `AttachmentImageAttributeID`,
                                      `CreatedByAgentID`, `CreatorID`, `ModifiedByAgentID`, `VisibilitySetByID`)
            VALUES ('{storename}', NULL, NULL, NULL, 
                    NULL, NULL, NULL,   '{get_pst_date_from_datetime(get_pst_time(file_created_datetime))}', '{guid}', TRUE, NULL, 
                    NULL, NULL, '{image_type}','{original_filename}', '{url}', 4, 
                    0, NULL, NULL, 41, '{get_pst_time_now_string()}',
                    '{get_pst_time_now_string()}', NULL, NULL, 0, NULL, NULL, 
                    95728, NULL, NULL, NULL)
    """)
    connect()
    cursor = cnx.cursor()
    cursor.execute(sql)
    cnx.commit()
    cursor.close()

def create_collection_object_attachment(attachment_id,collection_object_id,ordinal):
    connect()
    cursor = cnx.cursor()

    sql = (f"""INSERT INTO `collectionobjectattachment` 
        (`collectionmemberid`, 
        `ordinal`, 
        `remarks`, 
        `timestampcreated`,
        `timestampmodified`, 
        `version`, 
        `AttachmentID`, 
        `CollectionObjectID`,
        `CreatedByAgentID`, 
        `ModifiedByAgentID`)
    VALUES (
        4, 
        {ordinal}, 
        NULL, 
        '{get_pst_time_now_string()}', 
        '{get_pst_time_now_string()}',
        0, 
        {attachment_id}, 
        {collection_object_id}, 
        95728,
        NULL)""")
    cursor.execute(sql)
    cnx.commit()
    cursor.close()

def get_one_record(sql):
    connect()
    cursor = cnx.cursor()

    cursor.execute(sql)
    retval = cursor.fetchone()
    if retval is None:
        print(f"Warning: No results from: \n\n{sql}\n")
    else:
        retval = retval[0]
    cursor.close()
    return retval


def get_attachment_id(uuid):

    sql = f"select attachmentid from attachment where guid='{uuid}'"
    return get_one_record(sql)


def get_ordinal_for_collection_object_attachment(collection_object_id):
    sql = f"select max(ordinal) from collectionobjectattachment where CollectionObjectID={collection_object_id}"
    return get_one_record(sql)



def get_collectionobjectid_from_barcode(barcode):
    sql = f"select collectionobjectid  from collectionobject where catalognumber={barcode}"
    return get_one_record(sql)


def get_barcode_from_filepath(filepath):
    basename = os.path.basename(filepath)
    ints = re.findall(r'\d+', basename)
    if len(ints) == 0:
        raise InvalidFilenameError("Can't get barcode from filename")
    logging.debug(f"Processing file: {filepath} got barcode {ints[0]}")
    return ints[0]


def get_is_redacted(collection_object_id):
    sql = f"select YesNo1  from collectionobject where CollectionObjectID={collection_object_id}"
    if get_one_record(sql) is None:
        return False
    else:
        return True


# returns None if the object is missing.
def get_collection_object_id(filename):
    barcode = get_barcode_from_filepath(filename)
    collection_object_id = get_collectionobjectid_from_barcode(barcode)
    return collection_object_id


def import_to_database(filepath, attach_loc,url):
    connect()
    attachment_guid = uuid4()

    barcode = get_barcode_from_filepath(filepath)
    collection_object_id = get_collectionobjectid_from_barcode(barcode)
    file_created_datetime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))

    mime_type = None
    if filepath.lower().endswith('.tif') or filepath.lower().endswith('.tiff'):
        mime_type = 'image/tiff'
    if filepath.lower().endswith('.jpg') or filepath.lower().endswith('.jpeg'):
        mime_type = 'image/jpeg'
    if filepath.lower().endswith('.gif'):
        mime_type = 'image/gif'
    if filepath.lower().endswith('.png'):
        mime_type = 'image/png'
    if filepath.lower().endswith('.pdf'):
        mime_type = 'application/pdf'

    create_attachment(storename=attach_loc,
                      original_filename=os.path.basename(filepath),
                      file_created_datetime=file_created_datetime,
                      guid=attachment_guid,
                      image_type=mime_type,
                      url=url)
    attachment_id = get_attachment_id(attachment_guid)
    ordinal = get_ordinal_for_collection_object_attachment(collection_object_id)
    if ordinal is None:
        ordinal = 0
    else:
        ordinal += 1
    create_collection_object_attachment(attachment_id,collection_object_id,ordinal)
