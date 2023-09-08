import logging
import sys
import traceback
import sqlite3
import re

# from mysql.connector import errorcode
# import mysql.connector
import mariadb


class DatabaseInconsistentError(Exception):
    pass


class InvalidFilenameError(Exception):
    pass


class DataInvariantException(Exception):
    pass

# ector.connect(user=botany_importer_config.USER,
#                                               password=botany_importer_config.PASSWORD,
#                                               host=botany_importer_config.SPECIFY_DATABASE_HOST,
#                                               port=botany_importer_config.SPECIFY_DATABASE_PORT,
#                                               database=botany_importer_config.SPECIFY_DATABASE)
class DbUtils:
    def __init__(self, database_user, database_password, database_port, database_host, database_name):
        self.database_user = database_user
        self.database_password = database_password
        self.database_port = database_port
        self.database_host = database_host
        self.database_name = database_name
        self.logger = logging.getLogger('Client.dbutils')

        self.cnx = None
        self.connect()

    def reset_connection(self):

        self.logger.info(f"Resetting connection to {self.database_host}")
        if self.cnx:
            try:
                self.cnx.close()
            except Exception:
                pass
        self.connect()

    def connect(self):
        if self.cnx is None:
            self.logger.debug(f"Connecting to db {self.database_host}...")

            try:
                self.cnx = mariadb.connect(user=self.database_user,
                                           password=self.database_password,
                                           host=self.database_host,
                                           port=self.database_port,
                                           database=self.database_name)
            except mariadb.Error as err:
                print(f"MariaDB threw an error: {err}")
                if err.errno == 1045:
                    self.logger.error(f"Starting client...")
                    self.logger.error("SQL: Access denied")
                elif err.errno == 1049:
                    self.logger.error("Database does not exist")
                else:
                    self.logger.error(err)
                sys.exit(1)

            self.logger.info("Db connected")
        else:
            pass
            # self.logger.debug(f"Already connected db {self.database_host}...")

    # delarocamcas changed to buffered = True, so will work inside forloops
    def get_one_record(self, sql):
        self.connect()
        cursor = self.cnx.cursor(buffered=True)
        # print(self.database_host)
        # print(self.database_name)
        # print(self.database_port)
        try:
            cursor.execute(sql)
            retval = cursor.fetchone()

        except Exception as e:
            print(f"Exception thrown while processing sql: {sql}\n{e}\n", file=sys.stderr, flush=True)
            self.logger.error(traceback.format_exc())

            retval = None
        if retval is None:

            self.logger.warning(f"Warning: No results from: \n\n{sql}\n")
        else:
            retval = retval[0]
        cursor.close()
        return retval

    def create_record(self, sql):
        """used to run insert, update and create commands in mysql within DB"""
        self.connect()
        cursor = self.cnx.cursor(buffered=True)

        try:
            cursor.execute(sql)

        except Exception as e:
            print(f"Exception thrown while processing sql: {sql}\n{e}\n", file=sys.stderr, flush=True)
            self.logger.error(traceback.format_exc())

        cursor.close()

    def test_connector(self, sql):
        """create_table_record:
               general code for testing queries against sql lite DB
           args:
               sql: the verbatim sql string, or multi sql query string to send to sql lite database
        """
        connection = sqlite3.connect('cas_botanylite.db')
        cursor = connection.cursor()
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f"Exception thrown while processing sql: {sql}\n{e}\n", flush=True)
            self.logger.error(traceback.format_exc())
        connection.commit()
        cursor.close()
        connection.close()

    def get_records(self, query):
        cursor = self.get_cursor()
        cursor.execute(query)
        record_list = list(cursor.fetchall())
        self.logger.debug(f"get records SQL: {query}")
        cursor.close()
        return record_list

    def get_cursor(self):
        self.connect()
        return self.cnx.cursor(buffered=True)

    def execute(self, sql):
        cursor = self.get_cursor()
        self.logger.debug(f"SQL: {sql}")
        cursor.execute(sql)
        self.cnx.commit()
        cursor.close()

    def commit(self):
        self.cnx.commit()