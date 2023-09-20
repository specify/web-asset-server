"""test case of the CsvCreatePicturae class which runs a reduced init method to use in unittests"""
from image_client.importer import Importer
from image_client.picturae_csv_create import CsvCreatePicturae
from image_client import picturae_config

class TestCsvCreatePicturae(CsvCreatePicturae):
    def __init__(self, date_string):
        Importer.__init__(self, db_config_class=picturae_config, collection_name= "Botany")
        self.init_all_vars(date_string)

