"""this test module is for testing the populate_fields ,
    to make sure correct columns are assigned to variables before writing to db"""
import unittest
import pandas as pd
from tests.testing_tools import TestingTools
from tests.pic_importer_test_class import TestPicturaeImporter

class TestPopulateFields(unittest.TestCase, TestingTools):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.md5_hash = self.generate_random_md5()

    def setUp(self):
        """creating fake dataset to check if
          populate fields function assigns the strings and numbers"""
        self.test_picturae_importer = TestPicturaeImporter(date_string=self.md5_hash,
                                                         paths=self.md5_hash)
        data = {'CatalogNumber': ['123456'],
                'verbatim_date': ['March 21, 2008'],
                'start_date': ['3/21/2008'],
                'end_date': [pd.NA],
                'collector_number': [180024],
                'locality': ['Harden Lake'],
                'fullname': ['Castilleja miniata subsp. dixonii'],
                'taxname': ['dixonii'],
                'gen_spec': ['Castilleja miniata'],
                'qualifier': [pd.NA],
                'name_matched': ['Castillja miniata subsp. dixonii'],
                'Genus': ['Castilleja'],
                'Family': ['Orobanchaceae'],
                'Hybrid': [False],
                'accepted_author': ['Douglas ex hook'],
                'first_intra': ['Castilleja miniata subsp. dixonii'],
                'geography_string': ['Mariposa County, California, United States'],
                'county': 'Mariposa County',
                'state': 'California',
                'country': 'United States'}

        self.test_picturae_importer.record_full = pd.DataFrame(data)

    def test_assigned_to_variable(self):
        """tests whether correct integer and string values assigned to
           initialized variables from populate_fields"""
        for index, row in self.test_picturae_importer.record_full.iterrows():
            self.test_picturae_importer.populate_fields(row)
            self.assertEqual(self.test_picturae_importer.barcode, '000123456')
            self.assertEqual(self.test_picturae_importer.locality, 'Harden Lake')
            self.assertEqual(self.test_picturae_importer.GeographyID, 16490)
            self.assertEqual(self.test_picturae_importer.locality_id, 54)
            self.assertEqual(self.test_picturae_importer.first_intra, 'Castilleja miniata subsp. dixonii')

    def tearDown(self):
        """deleting PicturaeImporter class instance"""
        del self.test_picturae_importer