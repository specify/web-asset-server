"""This is an unittest file for the botany_importer.py"""
import os
import re
import logging
import filetype
from botany_importer import BotanyImporter
import shutil
import unittest
import logging
from testfixtures import LogCapture
from PIL import Image


class BotanyImporterTests(unittest.TestCase):

    def generate_test_directory(self):
        test_images_dir = '/Users/mdelaroca/Documents/sandbox_db/' \
                          'specify-sandbox/web-asset-server/image_client/test_images/'

        return test_images_dir

    def setUp(self):
        print("Setup Called!")
        # adding in botany importer
        self.botany_importer = BotanyImporter()
        # setting up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        self.log_capture = LogCapture()
        # create real image path
        test_images_dir = self.generate_test_directory()
        self.image_path_real = os.path.join(test_images_dir, "CAS0123456.JPG")
        image = Image.new("RGB", (100, 100), (255, 0, 0))
        image.save(self.image_path_real)

        # create incorrect image path for testing
        test_images_dir = self.generate_test_directory()
        self.image_path_false = os.path.join(test_images_dir, "CASABCDEFG.JPG")
        image = Image.new("RGB", (100, 100), (255, 0, 0))
        image.save(self.image_path_false)

    def test_build_filename_map(self):
        test_images_dir = self.generate_test_directory()
        file_name = "CASABCDEFG.JPG"
        error_path = os.path.join(test_images_dir, file_name.lower())
        base_path = os.path.basename(error_path)

        with LogCapture() as log_capture:
            self.botany_importer.build_filename_map(full_path=error_path)
            log_records = log_capture.records
            self.assertEqual(len(log_records), 1)
            self.assertEqual(log_records[0].levelname, "DEBUG")
            self.assertEqual(log_records[0].getMessage(),
                f"Rejected; no match: {base_path}")



    #def test_process_barcode(self):
       # self.botany_importer.process_barcode()

    def tearDown(self):
        print("tearDown called!")
        test_dir = self.generate_test_directory()

        os.remove(os.path.join(test_dir, "CASABCDEFG.JPG"))
        os.remove(os.path.join(test_dir,  "CAS0123456.JPG"))
        # removing logger capture
        self.log_capture.uninstall()

if __name__ == "__main__":
    unittest.main()
