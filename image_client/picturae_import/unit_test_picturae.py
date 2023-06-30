"""This file contains unit tests for picturae_import.py"""
import csv
import unittest
import random
import os
import shutil
from picturae_import import *
from faker import Faker
from datetime import date, timedelta

## need to find a way to prevent the fake folders using todays date in the setUP,
## from overwriting the contents of real folders
def test_date():
    test_date = date.today() - timedelta(days=365 * 20)
    return test_date


class WorkingDirectoryTests(unittest.TestCase):
    """TestFilePresent: a series of unit tests on the file_present
       function in picturae_import.py"""

    def test_working_directory(self):
        """test if user in correct working folder"""
        expected_relative = "picturae_import"
        current_dir = os.getcwd()
        _, last_directory = os.path.split(current_dir)
        self.assertEqual(expected_relative, last_directory)

    def test_directory(self):
        """tests if working folder contains correct subdirectory picturae_csv"""
        dir_pre = os.path.isdir("picturae_csv")
        self.assertTrue(dir_pre)

    def test_missing_folder_raise_error(self):
        """checks if incorrect sub_directory raises error"""
        with self.assertRaises(ValueError) as cm:
            file_present()
        self.assertEqual(str(cm.exception), f"subdirectory for {date.today()} not present")


class FilePathTests(unittest.TestCase):
    """tests paths for file_present function in fixture scope"""

    def setUp(self):

        print("setup called!")
        # create test directories

        date_string = test_date()

        expected_folder_path = 'picturae_csv/' + str(date_string) + '/picturae_folder(' + \
                               str(date_string) + ').csv'
        expected_specimen_path = 'picturae_csv/' + str(date_string) + '/picturae_specimen(' + \
                                 str(date_string) + ').csv'
        # making the directories
        os.makedirs(os.path.dirname(expected_folder_path), exist_ok=True)
        os.makedirs(os.path.dirname(expected_specimen_path), exist_ok=True)

        open(expected_folder_path, 'a').close()
        open(expected_specimen_path, 'a').close()

    def test_expected_path_date(self):
        """makes temporary folders, and csvs with today's date, to test function,
          when not overriden"""
        try:
            file_present()
        except Exception as e:
            self.fail(f"Exception raised: {str(e)}")

    def test_raise_specimen(self):
        date_string = test_date()
        # removing test path specimen
        os.remove('picturae_csv/' + str(date_string) + '/picturae_specimen(' +
                  str(date_string) + ').csv')
        with self.assertRaises(ValueError) as cm:
            file_present()
        self.assertEqual(str(cm.exception), "Specimen csv does not exist")

    def test_raise_folder(self):
        date_string = test_date()
        # removing test path folder
        os.remove('picturae_csv/' + str(date_string) + '/picturae_folder(' +
                  str(date_string) + ').csv')
        with self.assertRaises(ValueError) as cm:
            file_present()
        self.assertEqual(str(cm.exception), "Folder csv does not exist")

    def tearDown(self):
        """removes path for given created folder"""

        print("teardown called!")

        date_string = test_date()
        # create test directories

        expected_folder_path = 'picturae_csv/' + str(date_string) + '/picturae_folder(' + \
                                str(date_string) + ').csv'
        shutil.rmtree(os.path.dirname(expected_folder_path))



### class for testing csv_import function
# under construction
class CsvReadMergeTests(unittest.TestCase):

    # thinking of ways to simplify this setup function
    def setUp(self):
        """creates fake datasets with dummy columns to test import csv"""
        print("setup called!")
        # setting records and date list
        fake = Faker()
        num_records = 50
        date_string = test_date()
        # maybe create up a seperate function for setting up test directories
            # setting string paths
        path_type_list = ['folder', 'specimen']
        path_list = []
        for path_type in path_type_list:
            path = 'picturae_csv/' + str(date_string) + '/picturae_'+ str(path_type) + '(' + \
                    str(date_string) + ').csv'

        path_list.append(path)

        os.makedirs(os.path.dirname(path), exist_ok=True)

        open(path, 'a').close()
        # writing csvs
        for path in path_list:
            with open(path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                writer.writerow(['specimen_barcode', 'folder_barcode', 'path_jpg'])
                for i in range(num_records):
                    # to keep barcodes matching between folder and specimen csvs for merging
                    ordered_bar = 123456
                    specimen_bar = ordered_bar + i
                    # populating rest of columns with random data
                    folder_barcode = fake.random_number(digits=6)
                    jpg_path = fake.file_path(depth=random.randint(1, 5), category='image', extension='jpg')

                    # writing data to CSV
                    writer.writerow([specimen_bar, folder_barcode, jpg_path])
            print(f"Fake dataset {path} with {num_records} records created sucessfuly")


    def test_file_empty(self):
        """tests for every argument variation if dataset returns as empty"""
        date_string = test_date()
        self.assertEqual(csv_read_folder("folder", import_date=date_string).empty, False)
        self.assertEqual(csv_read_folder("specimen", import_date=date_string).empty, False)

    def test_file_colnumber(self):
        """tests for every argument variation, if correct # of columns"""
        date_string = test_date()
        self.assertEqual(len(csv_read_folder('folder', import_date=date_string).columns), 3)
        self.assertEqual(len(csv_read_folder('specimen', import_date=date_string).columns), 3)

    def test_barcode_column_present(self):
        """tests for every argument variation, if barcode column is present
           (test if column names loaded correctly, specimen_barcode being in any csv)"""
        date_string = test_date()
        self.assertEqual('specimen_barcode' in csv_read_folder('folder', date_string).columns, True)
        self.assertEqual('specimen_barcode' in csv_read_folder('specimen', date_string).columns, True)

    ### these tests are for the csv merge function
    def test_merge_num_columns(self):
        csv_specimen = csv_read_folder('specimen')
        csv_folder = csv_read_folder('folder')
        # -2 as merge function drops duplicate columns automatically
        self.assertEqual(len(csv_merge(csv_specimen, csv_folder).columns),
                         len(csv_specimen.columns) + len(csv_folder.columns) - 3)


    def test_index_length_matches(self):
        csv_folder = csv_read_folder('folder')
        csv_specimen = csv_read_folder('specimen')
        # test merge index before and after
        self.assertEqual(len(csv_merge(csv_folder, csv_specimen)),
                         len(csv_folder))

    def test_unequalbarcode_raise(self):
        csv_folder = csv_read_folder('folder')
        csv_specimen = csv_read_folder('specimen')
        csv_specimen['specimen_barcode'] = csv_specimen['specimen_barcode'] + 1
        with self.assertRaises(ValueError) as cm:
            csv_merge(csv_folder, csv_specimen)

        self.assertEqual(str(cm.exception), "Barcode Columns do not match!" )

    def test_output_isnot_empty(self):
        csv_folder = csv_read_folder('folder')
        csv_specimen = csv_read_folder('specimen')
        # testing output
        self.assertFalse(csv_merge(csv_folder, csv_specimen).empty)


    def tearDown(self):
        """deletes destination directories of dummy datasets"""
        print("teardown called!")
        date_string = test_date()

        folder_path = 'picturae_csv/' + str(date_string) + '/picturae_folder(' + \
                      str(date_string) + ').csv'

        print(os.path.dirname(folder_path))

        shutil.rmtree(os.path.dirname(folder_path))


if __name__ == "__main__":
    unittest.main()

