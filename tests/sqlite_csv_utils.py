"""derived class of SqlCsvTools in order to use sqlite protocols instead of
   standard database protocols"""
import sqlite3
from image_client import picturae_config
from image_client.sql_csv_utils import SqlCsvTools
class SqlLiteTools(SqlCsvTools):
    def __init__(self, sql_db):
        super().__init__(config=picturae_config)
        self.sqlite_db = sql_db
        self.connection = self.sql_db_connection()

    def sql_db_connection(self):
        """get sqlite connection"""
        return sqlite3.connect(database=self.sqlite_db)

    def get_record(self, sql):
        """sqlite replacement for get_one_record """
        curs = self.connection.cursor()
        try:
            curs.execute(sql)
        except Exception as e:
            raise ValueError(f"Exception thrown while processing sql: {sql}\n{e}\n")

        record = curs.fetchone()
        # closing connection
        if record is not None:
            return record[0]
        else:
            return record

    def get_cursor(self):
        """sqlite for get cursor"""
        return self.connection.cursor()

    def commit(self):
        """sqlite for commit"""
        return self.connection.commit()
