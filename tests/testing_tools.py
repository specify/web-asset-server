from datetime import date, timedelta
import random
from faker import Faker
import csv
import shutil
class TestingTools:
    def test_date(self):
        """test_date: creates an arbitrary date, 20 years in the past from today's date,
           to create test files for, so as not to overwrite current work
           ! if this code outlives 20 years of use I would be impressed"""
        unit_date = date.today() - timedelta(days=365 * 20)
        return str(unit_date)

    def create_fake_dataset(self, num_records: int, path_list: list):
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
