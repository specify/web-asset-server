"""base class for testing containing useful functions for Setup and Teardown"""
from faker import Faker
import csv
from PIL import Image
import os
import hashlib
import random
import string
from image_client import picturae_config
class TestingTools:

    def create_fake_dataset(self, num_records: int, path_list: list):
        """create_fake_dataset: creates a fake csv dataset with random data of a custom length,
                                can create multiple fake datasets with custom file_paths provided in a list.
            args:
                num_records: the amount of rows that will be in the fake dataset
                path_list: the number of paths at which to save the same number of fake datasets"""
        fake = Faker()
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
            print(f"Fake dataset {path} with {num_records} records created successfully")

    def create_test_images(self, barcode_list: list, date_string: str, color: str):
        """create_test_images:
                creates a number of standard test images in a range of barcodes,
                and with a specific date string
           args:
                barcode_list: a list or range() of barcodes that
                              you wish to create dummy images for.
                date_string: a date string , with which to name directory
                             in which to create and store the dummy images
        """
        image = Image.new('RGB', (200, 200), color=color)

        barcode_list = barcode_list
        for barcode in barcode_list:
            expected_image_path = f"picturae_img/PIC_{date_string}/CAS{barcode}.JPG"
            os.makedirs(os.path.dirname(expected_image_path), exist_ok=True)
            print(f"Created directory: {os.path.dirname(expected_image_path)}")
            image.save(expected_image_path)

    def generate_random_md5(self):
        """generate_random_md5: creates random combination of characters and digits, to create
                                a unique md5 code."""
        characters = string.ascii_letters + string.digits
        random_string = ''.join(random.choice(characters) for _ in range(16))
        md5_hash = hashlib.md5(random_string.encode()).hexdigest()

        return md5_hash
    def paths_generator(self, date: str):
        """paths_generator: function to generate paths variable to
           initialize the class PicturaeImporter.
           args:
              date: the date or md5 code used to initialize a test folder
        """
        picturae_config.PIC_SCAN_FOLDERS = [f"PIC_{date}"]
        paths = []
        for cur_dir in picturae_config.PIC_SCAN_FOLDERS:
            paths.append(os.path.join(picturae_config.PREFIX,
                                      picturae_config.PIC_PREFIX,
                                      cur_dir))

        return paths
