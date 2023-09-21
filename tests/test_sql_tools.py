"""This file contains unit tests for picturae_import.py"""
import unittest
import logging
import sqlite3
import numpy as np
import pandas as pd

from image_client.sql_csv_utils import insert_table_record
from tests.pic_importer_test_class import TestPicturaeImporter
import image_client.sql_csv_utils as scu
from tests.testing_tools import TestingTools
from image_client.casbotany_sql_lite import *
from image_client import time_utils
from uuid import uuid4
#
# class TestSQLlite(unittest.TestCase):
#     def test_casbotanylite(self):
#         connection = sqlite3.connect('cas_botanylite.db')
#         curs = connection.cursor()
#         curs.execute('''SELECT * FROM agent''')
#         num_columns = len(curs.description)
#         self.assertEqual(num_columns, 45)
#         curs.close()
#         connection.close()
#
# # class for testing csv_import function
# # too many redundant t4e


## this one should go to a test file for sql_db_utils
class TestSqlInsert(unittest.TestCase, TestingTools):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.md5_hash = self.generate_random_md5()
        self.logger = logging.getLogger("TestSqlInsert")
        self.connection = sql_lite_connection(db_name='casbotany_lite.db')

    def setUp(self):
        """setting up instance of PicturaeImporter"""
        self.test_picturae_importer = TestPicturaeImporter(date_string=self.md5_hash,
                                                           paths=self.md5_hash)

    def test_casbotanylite(self):
        "testing the whether the sqllite datbase can connect"
        connection = sqlite3.connect('cas_botanylite.db')
        curs = connection.cursor()
        curs.execute('''SELECT * FROM agent''')
        num_columns = len(curs.description)
        self.assertEqual(num_columns, 45)
        curs.close()
        connection.close()


    def test_sql_populate(self):
        """testing if the joining sql_operations in the
           function populate are creating the right sql string"""
        table_select = 'agent'
        column_list = ['AgentType', 'FirstName', 'MiddleInitial']
        value_list = [1, 'Fake', 'Name']

        column_list = ', '.join(column_list)
        value_list = ', '.join(f"'{value}'" if isinstance(value, str) else repr(value) for value in value_list)

        sql = f'''INSERT INTO {table_select} ({column_list}) VALUES({value_list})'''
        # assert statement
        expected_output = f'''INSERT INTO agent (AgentType, FirstName, MiddleInitial) VALUES(1, 'Fake', 'Name')'''
        self.assertEqual(sql, expected_output)


    def test_sql_string(self):
        """testing if create_sql_string
           creates the correct multi-value sql string for insert statements"""

        sql = scu.create_insert_statement(tab_name="codetab", val_list=[4, 5, "on mt"],
                                          col_list=['code4', 'code5', 'local'])

        self.assertEqual(sql, f'''INSERT INTO codetab (code4, code5, local) VALUES(4, 5, 'on mt');''')

        sql = scu.create_insert_statement(tab_name="cattab",
                                          val_list=[1, 2, 3, "cat"], col_list=['tax1', 'tax2', 'tax3', 'feline1'])

        self.assertEqual(sql, f'''INSERT INTO cattab (tax1, tax2, tax3, feline1) VALUES(1, 2, 3, 'cat');''')


    def test_create_locality(self):
        """testing create_locality function by
           recreating insert protocol for locality table, but with sqlLite DB"""

        localityname = f"2 miles from eastern side of Mt.Fake + {self.md5_hash}"

        column_list = ['TimestampCreated',
                       'TimestampModified',
                       'Version',
                       'GUID',
                       'SrcLatLongUnit',
                       'LocalityName',
                       'DisciplineID',
                       'GeographyID']

        value_list = [f"{time_utils.get_pst_time_now_string()}",
                      f"{time_utils.get_pst_time_now_string()}",
                      1,
                      f"{uuid4()}",
                      1,
                      localityname,
                      3,
                      256]

        # assigning row ids
        sql = scu.create_insert_statement(tab_name="locality", col_list=column_list,
                                          val_list=value_list)
        # testing insert table record
        insert_table_record(connection=self.connection, sql=sql, logger_int=self.logger, sqllite=True)
        # checking whether locality id created properly
        data_base_locality = casbotany_lite_getrecord(f'''SELECT `LocalityID` FROM locality WHERE 
                                                      `LocalityName` = "{localityname}"''')

        self.assertFalse(data_base_locality is None)

        # checking whether geocode present
        data_base_geo_code = casbotany_lite_getrecord(f'''SELECT `GeographyID` FROM locality WHERE 
                                                       `LocalityName` = "{localityname}"''')

        self.assertEqual(data_base_geo_code, 256)

    def test_collection_object(self):
        """test insert of collection object"""
        table = 'collectingevent'

        column_list = ['TimestampCreated',
                       'TimestampModified',
                       'Version',
                       'GUID',
                       'DisciplineID',
                       'StationFieldNumber',
                       'VerbatimDate',
                       'StartDate',
                       'EndDate',
                       'LocalityID',
                       'ModifiedByAgentID',
                       'CreatedByAgentID'
                       ]

        value_list = [f'{time_utils.get_pst_time_now_string()}',
                      f'{time_utils.get_pst_time_now_string()}',
                      0,
                      f'{uuid4()}',
                      3,
                      f'{123456}',
                      f'{"July 9, 1953"}',
                      f'{"07/09/1953"}',
                      f'{"07/09/1953"}',
                      f'{"14523"}',
                      f'{"95152"}',
                      f'{"95152"}'
                      ]

        # removing na values from both lists
        value_list, column_list = scu.remove_two_index(value_list, column_list)

        # assert that len val list and column list are equevalent.

        self.assertEqual(len(value_list), len(column_list))

        sql = scu.create_insert_statement(tab_name=table, col_list=column_list,
                                          val_list=value_list)

        insert_table_record(connection=self.connection, logger_int=self.logger, sql=sql, sqllite=True)


        station_field = casbotany_lite_getrecord(f'''SELECT `StationFieldNumber` FROM collectingevent WHERE 
                                                            `StationFieldNumber` = {123456}''')

        # asserting that station field number is in right column

        self.assertEqual('123456', station_field)


    def test_remove_two_index(self):
        """tests whether remove two index will drop
            correct amount of terms from value/column lists"""
        test_values = [1, 2, pd.NA, "cat", '', np.nan, None]
        test_col = ["col1", "col2", "col3", "col4", "col5", "col6", "col7"]

        test_values, test_col = scu.remove_two_index(value_list=test_values, column_list=test_col)

        self.assertEqual(len(test_col), len(test_values))
        self.assertEqual(len(test_values), 3)
        # using pd.isna() to avoid "boolean value of NA is ambiguous error
        for term in test_values:
            self.assertTrue(not pd.isna(term) and term not in [None, np.nan, ''])

    def tearDown(self):
        """deleting instance of PicturaeImporter"""
        del self.test_picturae_importer

if __name__ == "__main__":
    unittest.main()
