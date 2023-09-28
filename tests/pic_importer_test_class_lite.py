"""test case of the PicturaeImporter class which runs a reduced init and sqlite modified taxon_get function
    for taxon tree testing."""
import logging
from uuid import uuid4
from tests.casbotany_sql_lite import SqlLiteTools
from image_client.importer import Importer
from image_client.picturae_importer import PicturaeImporter
from image_client import picturae_config


class TestPicturaeImporterlite(PicturaeImporter):
    def __init__(self, date_string, paths):
        Importer.__init__(self, db_config_class=picturae_config, collection_name="Botany")
        self.init_all_vars(date_string=date_string, paths=paths)
        self.logger = logging.getLogger("TestPicturaeImporter")
        self.sql_csv_tools = SqlLiteTools()
        self.specify_db_connection = '../tests/casbotany_lite.db'

    # patched populate_fields function to avoid having to pull from the geography tree, for taxon tree tests
    def populate_fields(self, row):
        """populate_fields:
               this populates all the
               initialized data fields per row for input into database,
               make sure to check column list is correct so that the
               row indexes are assigned correctly.
           args:
                row: a row from a botany specimen csv dataframe containing the required columns

        """
        column_list = ['CatalogNumber', 'verbatim_date', 'start_date',
                       'end_date', 'collector_number', 'locality', 'fullname', 'taxname',
                       'gen_spec', 'qualifier', 'name_matched', 'Genus', 'Family', 'Hybrid', 'accepted_author',
                       'first_intra', 'county', 'state', 'country']
        # print(self.full_name)
        index_list = []
        for column in column_list:
            barcode_index = self.record_full.columns.get_loc(column)
            index_list.append(barcode_index)
        self.barcode = row[index_list[0]].zfill(9)
        self.verbatim_date = row[index_list[1]]
        self.start_date = row[index_list[2]]
        self.end_date = row[index_list[3]]
        self.collector_number = row[index_list[4]]
        self.locality = row[index_list[5]]
        self.full_name = row[index_list[6]]
        self.tax_name = row[index_list[7]]
        self.gen_spec = row[index_list[8]]
        self.qualifier = row[index_list[9]]
        self.name_matched = row[index_list[10]]
        self.genus = row[index_list[11]]
        self.family_name = row[index_list[12]]
        self.is_hybrid = row[index_list[13]]
        self.author = row[index_list[14]]
        self.first_intra = row[index_list[15]]

        guid_list = ['collecting_event_guid', 'collection_ob_guid', 'locality_guid', 'determination_guid']
        for guid_string in guid_list:
            setattr(self, guid_string, uuid4())
