"""This is an unittest file for the botany_importer.py"""
import botany_importer_config
from importer import Importer
import time_utils
from uuid import uuid4
import os
import re
import logging
import filetype
from botany_importer import BotanyImporter
import shutil
import unittest
from PIL import Image


class BotanyImporterTests(unittest.TestCase):

    def generate_test_directory(self):
        test_images_dir = '/Users/mdelaroca/Documents/sandbox_db/' \
                          'specify-sandbox/web-asset-server/image_client/test_images/.'

        return test_images_dir

    def SetUp(self):
        self.botany_importer = BotanyImporter()
        # create real image path
        test_images_dir = self.generate_test_directory()
        self.image_path_real = os.path.join(test_images_dir, "CAS0123456.JPG")
        image = Image.new("RGB", (100, 100), (255, 0, 0))
        image.save(self.image_path_real, "JPG")

        # create incorrect image path for testing
        test_images_dir = self.generate_test_directory()
        self.image_path_false = os.path.join(test_images_dir, "CASABCDEFG.JPG")
        image = Image.new("RGB", (100, 100), (255, 0, 0))
        image.save(self.image_path_false, "CASABCDEFG.JPG")

    def test_build_filename_map(self):
        self.botany_importer
        test_images_dir = self.generate_test_directory()
        error_path = os.path.join(test_images_dir, "CASABCDEFG.JPG")
        self.assertEqual(botany_importer.build_filename_map(self, full_path=error_path),
                         f"Rejected; no match: {error_path}")

    #def test_process_barcode(self):
       # self.botany_importer.process_barcode()

    def Teardown(self):
        shutil.rmtree(self.image_path_false)
        shutil.rmtree(self.image_path_real)


if __name__ == "__main__":
    unittest.main()
