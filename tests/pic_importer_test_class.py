"""test case of the PicturaeImporter class which runs a reduced init method to use in unittests"""
from image_client.importer import Importer
from image_client.picturae_importer import PicturaeImporter
from image_client import picturae_config
class TestPicturaeImporter(PicturaeImporter):
    def __init__(self, date_string, paths):
        Importer.__init__(self, db_config_class=picturae_config, collection_name="Botany")
        self.init_all_vars(date_string=date_string, paths=paths)