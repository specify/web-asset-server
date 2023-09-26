"""test case of the PicturaeImporter class which runs a reduced init and sqlite modified taxon_get function
    for taxon tree testing."""
import logging
from image_client.casbotany_sql_lite import *
from image_client.importer import Importer
from image_client.picturae_importer import PicturaeImporter
from image_client import picturae_config
class TestPicturaeImporterlite(PicturaeImporter):
    def __init__(self, date_string, paths):
        Importer.__init__(self, db_config_class=picturae_config, collection_name="Botany")
        self.init_all_vars(date_string=date_string, paths=paths)
        self.logger = logging.getLogger("TestPicturaeImporter")

    def taxon_get(self, name):
        taxon_id = casbotany_lite_getrecord(tab_name="taxon", id_col="TaxonID", key_col="FullName", match=name,
                                            match_type="string")
        return taxon_id