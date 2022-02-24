import mysql.connector
from mysql.connector import errorcode
import settings

cnx = None
from datetime import datetime

TIME_FORMAT_NO_OFFESET="%Y-%m-%d %H:%M:%S"
TIME_FORMAT=TIME_FORMAT_NO_OFFESET+"%z"
def log(msg):
    if settings.DEBUG:
        print(msg)

def get_cursor():
    if cnx is None:
        connect()
    return cnx.cursor()

def connect():
    global cnx
    try:
        cnx = mysql.connector.connect(user=settings.SQL_USER,
                                      password=settings.SQL_PASSWORD,
                                      host=settings.SQL_HOST,
                                      port=settings.SQL_PORT,
                                      database=settings.SQL_DATABASE)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            log("SQL: Access denied")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            log("Database does not exist")
        else:
            log(err)
        return False
    except Exception as ex:
        log(f"Unknown error:{ex}")
        return False
    log("Db connected")

    return True


def create_tables():
    TABLES = {}

    TABLES['images'] = (
        "CREATE TABLE if not exists `images`.`images` ("
        "   id int NOT NULL AUTO_INCREMENT primary key,"
        "  `original_filename` varchar(100),"
        "  `url` varchar(500),"
        "  `universal_url` varchar(500),"
        "  `original_path` varchar(500),"
        "  `redacted` BOOLEAN,"
        "  `internal_filename` varchar(500),"
        "  `notes` varchar(8192),"
        "  `datetime` datetime,"
        "  `collection` varchar(50)"
        ") ENGINE=InnoDB")

    cursor = get_cursor()

    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            log(f"Creating table {table_name}...")
            log(f"Sql: {TABLES[table_name]}")
            cursor.execute(table_description)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                log("already exists.")
            else:
                log(err.msg)
        else:
            log("OK")

    cursor.close()


def create_image_record(original_filename,
                        url,
                        internal_filename,
                        collection,
                        original_path,
                        notes,
                        redacted,
                        datetime_record):

    cursor = get_cursor()
    if original_filename is None:
        original_filename = "NULL"


    add_image = (f"""INSERT INTO images
                    (original_filename, url, universal_url, internal_filename, collection,original_path,notes,redacted,datetime)
                    values ("{original_filename}", "{url}", NULL, "{internal_filename}", "{collection}", "{original_path}", "{notes}", "{int(redacted)}", "{datetime_record.strftime(TIME_FORMAT_NO_OFFESET)}")""")
    log(f"Inserting image record. SQL: {add_image}")
    cursor.execute(add_image)
    cnx.commit()
    cursor.close()

def get_record(where_clause):

    cursor = get_cursor()

    query = f"""SELECT id, original_filename, url, universal_url, internal_filename, collection,original_path, notes, redacted, datetime
       FROM images 
       {where_clause}"""

    cursor.execute(query)
    record_list = []
    for (
            id, original_filename, url, universal_url, internal_filename, collection, original_path, notes,
            redacted, datetime_record) in cursor:
        record_list.append({'id': id,
                            'original_filename': original_filename,
                            'url': url,
                            'universal_url': universal_url,
                            'internal_filename': internal_filename,
                            'collection': collection,
                            'original_path': original_path,
                            'notes': notes,
                            'redacted': redacted,
                            # 'datetime': datetime_record, # TIME_STRING="%Y-%m-%d %H:%M:%S"
                            'datetime': datetime.strptime(datetime_record, TIME_FORMAT)
                            })
        print(f"of: {record_list}")

    cursor.close()
    return record_list

def get_image_record_by_internal_filename(internal_filename):
    cursor = get_cursor()

    query = f"""SELECT id, original_filename, url, universal_url, internal_filename, collection,original_path, notes, redacted, datetime
       FROM images 
       WHERE internal_filename = '{internal_filename}'"""

    cursor.execute(query)
    record_list = []
    for (id,
         original_filename,
         url,
         universal_url,
         internal_filename,
         collection,
         original_path,
         notes,
         redacted,
         datetime_record) in cursor:
        record_list.append({'id': id,
                            'original_filename': original_filename,
                            'url': url,
                            'universal_url': universal_url,
                            'internal_filename': internal_filename,
                            'collection': collection,
                            'original_path': original_path,
                            'notes': notes,
                            'redacted': redacted,
                            'datetime': datetime_record.strftime(TIME_FORMAT)
                            })
        print(f"of: {record_list}")

    cursor.close()
    return record_list

def get_image_record_by_original_filename(original_filename,exact,collection):

    cursor = get_cursor()
    if exact:
        query = f"""SELECT id, original_filename, url, universal_url, internal_filename, collection,original_path, notes, redacted, datetime
        FROM images 
        WHERE original_filename = '{original_filename}'"""
    else:
        query = f"""SELECT id, original_filename, url, universal_url, internal_filename, collection,original_path, notes, redacted, datetime
        FROM images 
        WHERE original_filename LIKE '{original_filename}'"""
    if collection is not None:
        query += f""" AND collection = '{collection}'"""
    log(f"Query get_image_record_by_original_filename: {query}")

    cursor.execute(query)
    record_list = []
    for (
    id, original_filename, url, universal_url, internal_filename, collection, original_path, notes, redacted,datetime_record) in cursor:
        record_list.append({'id': id,
                            'original_filename': original_filename,
                            'url': url,
                            'universal_url': universal_url,
                            'internal_filename': internal_filename,
                            'collection': collection,
                            'original_path': original_path,
                            'notes': notes,
                            'redacted': redacted,
                            'datetime': datetime_record
                            })
        log(f"Found at least one record: {record_list[-1]}")

    cursor.close()
    return record_list


def delete_image_record(internal_filename):
    cursor = get_cursor()

    delete_image = (f"""delete from images where internal_filename='{internal_filename}' """)

    log(f"deleting image record. SQL: {delete_image}")
    cursor.execute(delete_image)
    cnx.commit()
    cursor.close()


def get_collection_list():
    cursor = get_cursor()

    query = f"""select collection from collection"""

    cursor.execute(query)
    collection_list=[]
    for (collection) in cursor:
        collection_list.append(collection)
