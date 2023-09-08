"""This is an unittest file for the botany_importer.py"""
import os
import re
import logging
import filetype
from unittest.mock import Mock
from mock import patch
from botany_importer import BotanyImporter
import unittest
import logging
from testfixtures import LogCapture
from PIL import Image


class BotanyImporterTests(unittest.TestCase):

    def generate_test_directory(self):
        test_images_dir = '/image_client/test_images/'

        return test_images_dir

    def setUp(self):
        """ The setup function the environment by
            creating three test images, some have incorrect
            data in order to test logger returns"""
        # adding in botany importer
        self.botany_importer = BotanyImporter()
        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.log_capture = LogCapture()
        # create real image path and incorrect image path
        path_list = ["CAS0123456.JPG", "CASABCDEFG.JPG", "CAS999999991.JPG"]
        test_images_dir = self.generate_test_directory()
        for picture in path_list:
            self.image_path_real = os.path.join(test_images_dir, picture)
            image = Image.new("RGB", (100, 100), (255, 0, 0))
            image.save(self.image_path_real)

    def test_build_filename_map_barcodeerror(self):
        """test_build_filename_map_barcode_error:
            this unittest tests checks when the .jpg name
            does not match the regex"""
        test_images_dir = self.generate_test_directory()
        file_name = "CASABCDEFG.JPG"
        error_path = os.path.join(test_images_dir, file_name.lower())
        base_path = os.path.basename(error_path)

        with LogCapture() as log_capture:
            self.botany_importer.build_filename_map(full_path=error_path)
            log_records = log_capture.records
            # checks correct amount fo logger records
            self.assertEqual(len(log_records), 1)
            # checks correct verbosity level
            self.assertEqual(log_records[0].levelname, "DEBUG")
            # checks the message logger message string
            self.assertEqual(log_records[0].getMessage(), f"Rejected; no match: {base_path}")

    def test_build_filename_mappingappend(self):
        """test_build_filename_mappingappend: checks,
           whether correct successful logger message returns,
           and whether the barcode map was correctly appended"""
        test_images_dir = self.generate_test_directory()
        file_name = "CAS0123456.JPG"
        barcode = "123456"
        barcode = barcode.zfill(9)
        real_path = os.path.join(test_images_dir.lower(), file_name.lower())
        base_path = os.path.basename(real_path)

        with LogCapture() as log_capture:
            self.botany_importer.build_filename_map(full_path=real_path)
            log_records = log_capture.records
            # 2 due to get_first_digits giving a log record
            # checks correct amount fo logger records
            self.assertEqual(len(log_records), 2)

            # assert correct level name
            self.assertEqual(log_records[0].levelname, "DEBUG")

            # assert get first digits working
            self.assertEqual(
                log_records[0].getMessage(),
                f"extracting digits from {base_path} to get {barcode}")

            # assert correct log returned for success
            self.assertEqual(
                log_records[1].getMessage(),
                f"Adding filename to mappings set: {base_path}   barcode: {barcode}")

        # asserting the barcode map is appended with a new element
        self.assertEqual(self.botany_importer.barcode_map[barcode][0], real_path)

    def test_process_barcode_none(self):
        """when barcode is input as None,
           does the correct loger message return"""
        with LogCapture() as log_capture:
            self.botany_importer.process_barcode(barcode=None, filepath_list=[])
            log_records = log_capture.records
            # assert correct num records
            self.assertEqual(len(log_records), 1)

            self.assertEqual(log_records[0].levelname, "DEBUG")

            self.assertEqual(
                log_records[0].getMessage(), f"No barcode; skipping")

    @patch('botany_importer.BotanyImporter.create_skeleton', return_value='None')
    @patch('botany_importer.Importer.import_to_imagedb_and_specify', return_value='None')
    def test_process_barcode_missing_collection_object(self, test_skeleton, test_img_db):
        """tests whether the correct logger message of creating skeleton,
            is returned when a barcode not in database in tested"""
        # Create an instance of the BotanyImporter class
        test_dir = self.generate_test_directory()
        file_name = "CAS999999991.JPG"
        barcode = "999999991"
        full_path = os.path.join(test_dir.lower(), file_name.lower())

        with LogCapture() as log_capture:
            self.botany_importer.process_barcode(barcode=barcode, filepath_list=[full_path])
            log_records = log_capture.records
            # assert correct num records
            self.assertEqual(len(log_records), 4)

            self.assertEqual(log_records[2].levelname, "DEBUG")

            self.assertEqual(log_records[2].getMessage(),
                             f"No record found for catalog number {barcode}, creating skeleton.")

    @patch('botany_importer.BotanyImporter.create_skeleton', return_value=None)
    @patch('botany_importer.Importer.import_to_imagedb_and_specify', return_value=None)
    def test_remove_filenames_list(self, test_skeleton, test_img_db):
        """tests whether the file_list is cleaned of created records"""
        instance = BotanyImporter()
        test_dir = self.generate_test_directory()
        file_name = "CAS0688729.JPG"
        barcode = "688729"
        full_path = os.path.join(test_dir.lower(), file_name.lower())
        # creating instance of filepath_list
        filepath_list = [full_path]
        test_list = [full_path]

        new_list = instance.remove_imagedb_imported_filenames_from_list(filepath_list)
        self.assertEqual(len(new_list), 0)

        self.assertNotEqual(new_list, test_list)


    def tearDown(self):
        """deletes test files"""
        test_dir = self.generate_test_directory()

        os.remove(os.path.join(test_dir, "CASABCDEFG.JPG"))
        os.remove(os.path.join(test_dir, "CAS0123456.JPG"))
        os.remove(os.path.join(test_dir, "CAS999999991.JPG"))

        # removing logger capture
        self.log_capture.uninstall()

if __name__ == "__main__":
    unittest.main()
