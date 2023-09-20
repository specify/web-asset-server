import unittest
import os
from tests.testing_tools import TestingTools
from tests.pic_importer_test_class import TestPicturaeImporter
import shutil

os.chdir("./image_client")
class HideFilesTest(unittest.TestCase,TestingTools):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.md5_hash = self.generate_random_md5()
    def setUp(self):
        """creating test images in test_date folder, in order to test
           file_hide and file_unhide functions, creates 3 sample test
           images with sample barcodes"""

        # print("setup called!")
        paths = self.paths_generator(date=self.md5_hash)
        # create test directories

        self.create_test_images(barcode_list=[123456, 123457, 123458],
                                date_string=self.md5_hash, color='red')

        self.expected_image_path = f"picturae_img/PIC_{self.md5_hash}/CAS{123456}.JPG"

        # initializing
        self.TestPicturaeImporter = TestPicturaeImporter(date_string=self.md5_hash, paths=paths)

        self.TestPicturaeImporter.image_list = [f"picturae_img/PIC_{self.md5_hash}/CAS123456.JPG"]

    def test_file_hide(self):
        """testing whether file_hide hides files not in barcode list"""
        self.TestPicturaeImporter.hide_unwanted_files()
        files = os.listdir(f"picturae_img/PIC_{self.md5_hash}")
        self.assertTrue('CAS123456.JPG' in files)
        self.assertTrue('.hidden_CAS123457.JPG')

    def test_file_unhide(self):
        """testing whether files are correctly unhidden after running hide_unwanted_files"""
        self.TestPicturaeImporter.hide_unwanted_files()
        self.TestPicturaeImporter.unhide_files()
        files = os.listdir(f"picturae_img/PIC_{self.md5_hash}")
        self.assertEqual(set(files), {'CAS123456.JPG', 'CAS123457.JPG', 'CAS123458.JPG'})

    def tearDown(self):
        """deleting test directory and instance of PicturaeImporter class"""

        shutil.rmtree(os.path.dirname(self.expected_image_path))

        del self.TestPicturaeImporter