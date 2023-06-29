"""This file contains unit tests for picturae_import.py"""
from picturae_import import *
import unittest
import os
from datetime import date


class TestFilePresent(unittest.TestCase):
    """TestFilePresent: a series of unit tests on the file_present
       function in picturae_import.py"""
    def test_working_directory(self):
        """test if in correct working folder"""
        expected_relative = "picturae_import"
        current_dir = os.getcwd()
        _, last_directory = os.path.split(current_dir)
        self.assertEqual(expected_relative, last_directory)

    def test_directory(self):
        """test if working folder contains correct subdirectory"""
        dir_pre = os.path.isdir("picturae_csv")
        self.assertTrue(dir_pre)

    def test_files_confirm(self):
        """test if test folders with input errors produce correct output"""
        self.assertEqual(file_present(date_override=True, new_date="2023-6-28"), 2)
        self.assertEqual(file_present(date_override=True, new_date="2023-6-27"), 1)
        self.assertEqual(file_present(date_override=True, new_date="2023-2-18"), 0)

    def raise_error(self):
        """checks if incorrect sub_directory raises error"""
        with self.assertRaises(ValueError) as cm:
            file_present()
        self.assertEqual(str(cm.exception), f"subdirectory for {date.today()} not present")


if __name__ == "__main__":
    unittest.main()
