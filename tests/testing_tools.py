from datetime import date, timedelta
import random
from faker import Faker
import csv
from PIL import Image
import os
import shutil
class TestingTools:
    def test_date(self):
        """test_date: creates an arbitrary date, 20 years in the past from today's date,
           to use for testing, so as not to accidentally overwrite or modify current work."""
        unit_date = date.today() - timedelta(days=365 * 100)
        return str(unit_date)

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
