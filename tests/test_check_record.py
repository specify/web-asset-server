"""tests to test the record present, barcode present and image present functions."""
import unittest
import picturae_csv_create as pcc
import pandas as pd
from tests.testing_tools import TestingTools

class DatabaseChecks(unittest.TestCase, TestingTools):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.md5_hash = self.generate_random_md5()
    def setUp(self):
        """creates fake dataset with dummy columns,
          that have a small subset of representative real column names,
        """
        # initializing
        self.CsvCreatePicturae = pcc.CsvCreatePicturae(date_string=self.md5_hash, istesting=True)

        # creating dummy dataset, one mistake 530923 != 530924 inserted on purpose
        # the test barcode that is set to return a false is 58719322,
        # an unrealistically high barcode higher than digit limit in DB #
        data = {'CatalogNumber': ['530923', '58719322', '8708'],
                'image_path': ['picturae_img/cas0530924.jpg',
                               'picturae_img/cas58719322.jpg',
                               'picturae_img/cas0008708.jpg'],
                'folder_barcode': ['2310_2', '2310_2', '2312_2']}

        self.CsvCreatePicturae.record_full = pd.DataFrame(data)

    def test_barcode_present(self):
        """checks whether boolean column added for record present"""
        self.CsvCreatePicturae.barcode_has_record()
        # checks whether boolean column correctly added
        self.assertEqual(len(self.CsvCreatePicturae.record_full.columns), 4)
        # checks that no NAs were dropped
        self.assertEqual(len(self.CsvCreatePicturae.record_full), 3)
        # checks that the correct boolean order is returned
        test_list = list(self.CsvCreatePicturae.record_full['barcode_present'])
        self.assertEqual(test_list, [True, False, True])

    def test_if_barcode_match(self):
        """tests if there is a barcode in the barcode
           column that does not match the barcode in the img file name,
           the correct boolean is returned"""
        self.CsvCreatePicturae.check_barcode_match()
        test_list = list(self.CsvCreatePicturae.record_full['is_barcode_match'])
        self.assertEqual([False, True, True], test_list)

    def test_image_has_record(self):
        """tests if image_has_record returns true for
           one real attachment in test df"""
        self.CsvCreatePicturae.image_has_record()
        test_list = list(self.CsvCreatePicturae.record_full['image_present'])
        self.assertEqual([True, False, False], test_list)


    def tearDown(self):
        del self.CsvCreatePicturae