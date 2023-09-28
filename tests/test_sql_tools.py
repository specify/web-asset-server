"""This file contains unit tests for picturae_import.py"""
import unittest
import sqlite3
import logging
import numpy as np
import pandas as pd
import os
from image_client.picturae_import_utils import remove_two_index
from tests.pic_importer_test_class import TestPicturaeImporter
from tests.testing_tools import TestingTools
from image_client import time_utils
from uuid import uuid4
import shutil

os.chdir("./image_client")

class TestSqlInsert(unittest.TestCase, TestingTools):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.md5_hash = self.generate_random_md5()
        self.logger = logging.getLogger("TestSqlInsert")
        self.sqlite_connection = '../tests/casbotany_lite.db'

    def setUp(self):
        """setting up instance of PicturaeImporter"""
        self.test_picturae_importer = TestPicturaeImporter(date_string=self.md5_hash,
                                                           paths=self.md5_hash)

        self.sql_csv_tools = self.test_picturae_importer.sql_csv_tools

        self.sqlite_csv_tools = self.test_picturae_importer.sqlite_csv_tools

        self.specify_db_connection = self.test_picturae_importer.specify_db_connection

        shutil.copyfile("../tests/casbotany_lite.db", "../tests/casbotany_backup.db")

    def test_casbotanylite(self):
        "testing the wether the sqlite datbase can connect"
        connection = sqlite3.connect('../tests/casbotany_lite.db')
        curs = connection.cursor()
        curs.execute('''SELECT * FROM agent''')
        num_columns = len(curs.description)
        self.assertEqual(num_columns, 45)
        curs.close()
        connection.close()

    def test_sql_string(self):
        """testing if create_sql_string
           creates the correct multi-value sql string for insert statements"""

        sql = self.sql_csv_tools.create_insert_statement(tab_name="codetab", val_list=[4, 5, "on mt"],
                                                         col_list=['code4', 'code5', 'local'])

        self.assertEqual(sql, f'''INSERT INTO codetab (code4, code5, local) VALUES(4, 5, 'on mt');''')

        sql = self.sql_csv_tools.create_insert_statement(tab_name="cattab",
                                                         val_list=[1, 2, 3, "cat"],
                                                         col_list=['tax1', 'tax2', 'tax3', 'feline1'])

        self.assertEqual(sql, f'''INSERT INTO cattab (tax1, tax2, tax3, feline1) VALUES(1, 2, 3, 'cat');''')

    def test_remove_two_index(self):
        """tests whether remove two index will drop
            correct amount of terms from value/column lists"""
        test_values = [1, 2, pd.NA, "cat", '', np.nan, None]
        test_col = ["col1", "col2", "col3", "col4", "col5", "col6", "col7"]

        test_values, test_col = remove_two_index(value_list=test_values, column_list=test_col)

        self.assertEqual(len(test_col), len(test_values))
        self.assertEqual(len(test_values), 3)
        # using pd.isna() to avoid "boolean value of NA is ambiguous error
        for term in test_values:
            self.assertTrue(not pd.isna(term) and term not in [None, np.nan, ''])

    def test_create_locality(self):
        """testing create_locality function by
           recreating insert protocol for locality table, but with sqlite DB"""

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
        sql = self.sql_csv_tools.create_insert_statement(tab_name="locality", col_list=column_list,
                                                         val_list=value_list)
        # testing insert table record
        self.sqlite_csv_tools.insert_table_record(connection=self.sqlite_connection,
                                                   sql=sql, logger_int=self.logger)
        # checking whether locality id created properly
        data_base_locality = self.sqlite_csv_tools.get_one_match(connection=self.sqlite_connection,
                                                              id_col="LocalityID", tab_name="locality",
                                                              key_col="LocalityName", match=localityname,
                                                              match_type="string")

        self.assertFalse(data_base_locality is None)

        # checking whether geocode present

        data_base_geo_code = self.sqlite_csv_tools.get_one_match(connection=self.sqlite_connection,
                                                              id_col="GeographyID", tab_name="locality",
                                                              key_col="LocalityName", match=localityname,
                                                              match_type="string")

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
        value_list, column_list = remove_two_index(value_list, column_list)

        # assert that len val list and column list are equivalent.

        self.assertEqual(len(value_list), len(column_list))

        sql = self.sql_csv_tools.create_insert_statement(tab_name=table, col_list=column_list,
                                                         val_list=value_list)

        self.sqlite_csv_tools.insert_table_record(connection=self.sqlite_connection,
                                                   logger_int=self.logger, sql=sql)

        station_field = self.sqlite_csv_tools.get_one_match(connection=self.sqlite_connection,
                                                             id_col="StationFieldNumber", tab_name="collectingevent",
                                                             key_col="StationFieldNumber",
                                                             match=123456, match_type="integer")

        # asserting that station field number is in right column

        self.assertEqual('123456', station_field)

    def tearDown(self):
        """deleting instance of PicturaeImporter"""
        del self.test_picturae_importer
        shutil.copyfile("../tests/casbotany_backup.db", "../tests/casbotany_lite.db")
        os.remove("../tests/casbotany_backup.db")

if __name__ == "__main__":
    unittest.main()
