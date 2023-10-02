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

    def setUp(self):
        """setting up instance of PicturaeImporter"""
        self.test_picturae_importer = TestPicturaeImporter(date_string=self.md5_hash,
                                                           paths=self.md5_hash)

        self.sql_csv_tools = self.test_picturae_importer.sql_csv_tools

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

        self.test_picturae_importer.locality_guid = uuid4()
        self.test_picturae_importer.locality = f"2 miles from eastern side of Mt.Fake + {self.md5_hash}"
        self.test_picturae_importer.GeographyID = 256
        self.test_picturae_importer.create_by_agent = 999987

        self.test_picturae_importer.create_locality_record()

        data_base_locality = self.sql_csv_tools.get_one_match(id_col="LocalityID", tab_name="locality",
                                                              key_col="LocalityName",
                                                              match=self.test_picturae_importer.locality,
                                                              match_type="string")

        self.assertFalse(data_base_locality is None)

        # checking whether geocode present

        data_base_geo_code = self.sql_csv_tools.get_one_match(id_col="GeographyID", tab_name="locality",
                                                              key_col="LocalityName",
                                                              match=self.test_picturae_importer.locality,
                                                              match_type="string")

        self.assertEqual(data_base_geo_code, self.test_picturae_importer.GeographyID)

    def test_collection_object(self):
        """test insert of collection object"""
        self.test_picturae_importer.barcode = 99999998
        self.test_picturae_importer.collection_ob_guid = uuid4()
        self.test_picturae_importer.created_by_agent = 999987

        self.test_picturae_importer.create_collection_object()

        collection_ob_guid = self.sql_csv_tools.get_one_match(id_col="GUID", tab_name="collectionobject",
                                                               key_col="CatalogNumber",
                                                               match=self.test_picturae_importer.barcode,
                                                               match_type="integer")

        catalog_number = self.sql_csv_tools.get_one_match(id_col="CatalogNumber", tab_name="collectionobject",
                                                          key_col="GUID",
                                                          match=self.test_picturae_importer.collection_ob_guid,
                                                          match_type="string")

        # asserting that station field number is in right column

        self.assertEqual(str(self.test_picturae_importer.collection_ob_guid), collection_ob_guid)

        self.assertEqual(str(self.test_picturae_importer.barcode), catalog_number)

    def tearDown(self):
        """deleting instance of PicturaeImporter"""
        del self.test_picturae_importer
        shutil.copyfile("../tests/casbotany_backup.db", "../tests/casbotany_lite.db")
        os.remove("../tests/casbotany_backup.db")

if __name__ == "__main__":
    unittest.main()
