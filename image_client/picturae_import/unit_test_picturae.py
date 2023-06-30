"""This file contains unit tests for picturae_import.py"""
from picturae_import import *
import unittest
import pytest
import os
import shutil
from datetime import date, timedelta


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
        # setting date
        old_date = date.today() - timedelta(days=365 * 20)

        today_date = date.today()
        # create test directories

        date_list = [str(old_date), str(today_date)]

        for date_string in date_list:

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
        # removing test path specimen
        os.remove('picturae_csv/' + str(date.today()) + '/picturae_specimen(' +
                  str(date.today()) + ').csv')
        with self.assertRaises(ValueError) as cm:
            file_present()
        self.assertEqual(str(cm.exception), "Specimen csv does not exist")

    def test_raise_folder(self):
        # removing test path folder
        os.remove('picturae_csv/' + str(date.today()) + '/picturae_folder(' +
                  str(date.today()) + ').csv')
        with self.assertRaises(ValueError) as cm:
            file_present()
        self.assertEqual(str(cm.exception), "Folder csv does not exist")


    def test_files_override_both(self):
        """tests if test folders work for override= True"""
        twenty_years = date.today() - timedelta(days=365 * 20)

        # writing assert statement
        try:
            file_present(date_override=True, new_date=twenty_years)
        except Exception as ex:
            self.fail(f"Exception raised: {str(ex)}")

    def test_raise_specimen_override(self):
        twenty_years = date.today() - timedelta(days=365 * 20)

        os.remove('picturae_csv/' + str(twenty_years) + '/picturae_specimen(' +
                  str(twenty_years) + ').csv')

        with self.assertRaises(ValueError) as cm:
            file_present(date_override=True, new_date=twenty_years)
        self.assertEqual(str(cm.exception), "Specimen csv does not exist")

    def test_raise_folder_override(self):
        twenty_years = date.today() - timedelta(days=365 * 20)

        os.remove('picturae_csv/' + str(twenty_years) + '/picturae_folder(' +
                  str(twenty_years) + ').csv')

        with self.assertRaises(ValueError) as cm:
            file_present(date_override=True, new_date=twenty_years)

        self.assertEqual(str(cm.exception), "Folder csv does not exist")


    def tearDown(self):
        """removes path for given created folder"""

        print("teardown called!")

        old_date = date.today() - timedelta(days=365 * 20)

        today_date = date.today()

        date_list = [str(old_date), str(today_date)]
        # create test directories

        for date_string in date_list:
            expected_folder_path = 'picturae_csv/' + str(date_string) + '/picturae_folder(' + \
                                   str(date_string) + ').csv'

            shutil.rmtree(os.path.dirname(expected_folder_path))



### class for testing csv_import function
# under construction
# class CsvReaderTests(unittest.TestCase):
#
#     def setUP():

    #def test_file_empty(self):





if __name__ == "__main__":
    unittest.main()
