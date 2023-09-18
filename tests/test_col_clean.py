"""tests the rename_cols function, to make sure correct column names are assigned"""
import unittest
import os
import pandas as pd
import picturae_csv_create as pcc
from tests.testing_tools import TestingTools

os.chdir("./image_client")

class ColNamesTest(unittest.TestCase, TestingTools):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.md5_hash = self.generate_random_md5()
    def setUp(self):
        """creates dummy dataset with representative column names"""
        # initializing class
        self.CsvCreatePicturae = pcc.CsvCreatePicturae(date_string=self.md5_hash, istest=True)
        # creating dummy dataset
        numb_range = list(range(1, 101))
        column_names = ['application_batch', 'csv_batch', 'object_type', 'folder_barcode',
                        'specimen_barcode', 'filed_as_family', 'barcode_info', 'path_jpg',
                        'Taxon ID', 'Family', 'Genus', 'Species', 'Qualifier', 'Author',
                        'Rank1', 'Epithet 1', 'Rank 2', 'Epithet 2', 'Rank 2.1', 'Epithet 2.1',
                        'Hybrid', 'Hybrid Genus', 'Hybrid Species', 'Hybrid Rank 1',
                        'Hybrid Epithet 1', 'Hybrid Level',
                        'collector_number', 'collector_first_name 1', 'collector_middle_name 1',
                        'collector_last_name 1', 'collector_first_name 2',
                        'collector_middle_name 2', 'collector_last_name 2',
                        'collector_first_name 3', 'collector_middle_name 3',
                        'collector_last_name 3', 'collector_first_name 4',
                        'collector_middle_name 4', 'collector_last_name 4',
                        'collector_first_name 5', 'collector_middle_name 5',
                        'collector_last_name 5', 'Country', 'State', 'County', 'Locality',
                        'Verbatim Date', 'Start Date', 'End Date']
        new_df = {column_names[i]: numb_range for i in range(49)}

        # adding in fake notes and feedback columns,
        # so they can be filtered without raise.
        new_df['Notes'] = pd.NA
        new_df['Feedback'] = pd.NA

        self.CsvCreatePicturae.record_full = pd.DataFrame(new_df)

    def test_if_id_cols(self):
        """test_if_id_col: tests whether certain essential
           ID columns present. Also tests, wether name columns correctly
           reformated
        """
        self.CsvCreatePicturae.csv_colnames()
        csv_columns = self.CsvCreatePicturae.record_full.columns
        column_names = ['collector_number', 'RankID',
                        'CatalogNumber', 'collector_last_name1',
                        'collector_first_name5']
        self.assertTrue(all(column in csv_columns for column in column_names))

    def test_if_nas(self):
        """test_if_nas: test if any left-over columns contain only NAs"""
        self.CsvCreatePicturae.csv_colnames()
        self.record_full = self.CsvCreatePicturae.record_full.dropna(axis=1, how='all')
        self.assertEqual(len(self.record_full.columns), len(self.record_full.columns))

    def tearDown(self):
        del self.CsvCreatePicturae
