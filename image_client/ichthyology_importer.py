import ich_importer_config
from importer import Importer
import filetype
import os
import re
import logging
from dir_tools import DirTools


logging.basicConfig(level=logging.DEBUG)
sla = os.path.sep
ICH_PREFIX = f'ichthyology{sla}images{sla}'
ICH_SCAN_FOLDERS = ['AutomaticSpecifyImport']
'''
ICH_SCAN_FOLDERS = [f'CAS types{sla}Archive{sla}illustrations',
                    f'CAS types{sla}Archive{sla}photographs',
                    f'CAS types{sla}Archive{sla}radiographs',
                    f'CAS types{sla}Non-primary types{sla}illustrations',
                    f'CAS types{sla}Non-primary types{sla}photographs',
                    f"CAS types{sla}Non-primary types{sla}radiographs",
                    f'CAS other{sla}illustrations',
                    f'CAS other{sla}photographs',
                    f'CAS other{sla}radiographs']
'''

class FilenameFormatException(Exception):
    pass

class IchthyologyImporter(Importer):
    def __init__(self):
        self.logger = logging.getLogger('Client.IchthyologyImporter')

        self.collection_name = "Ichthyology"

        super().__init__(ich_importer_config)
        self.catalog_number_map = {}

        dir_tools = DirTools(self.build_filename_map)

        prefix = ich_importer_config.IMAGE_DIRECTORY_PREFIX


        for cur_dir in ICH_SCAN_FOLDERS:
            cur_dir = os.path.join(prefix, ICH_PREFIX, cur_dir)
            print(f"Scanning: {cur_dir}")
            dir_tools.process_files_or_directories_recursive(cur_dir)

        # outfile = open(FILENAME,'wb')
        # pickle.dump(ichthyology_importer.catalog_number_map, outfile)
        # else:
        #     ichthyology_importer.catalog_number_map = pickle.load(open(FILENAME, "rb"))

        self.process_loaded_files()

    def get_catalog_number(self, filename):
        #  the institution and collection codes before the catalog number
        #  either CAS-ICH-###### or CAS-SU-#####.
#        pattern = re.compile("(CAS)?(SU)?(ICH)?([0-9]*)")
        pattern = re.compile("cas-(ich)?(su)?-([0-9]+)")
        rematch = pattern.match(filename)
        if rematch is None:
            print (f"No matches for filename: {filename}")
            raise FilenameFormatException()
        list(rematch.groups())
        number = rematch.groups()[2]
        if number is None or number == '':
            return None, None
        number = int(number)
        collection = None
        if rematch.groups()[0] is not None:
            collection = "CAS-ICH"
        if rematch.groups()[1] is not None:
            collection = "CAS-SU "

        number = str(number).zfill(6)

        return f'{number}', collection

    def build_filename_map(self, full_path):
        full_path = full_path.lower()
        # logging.debug(f"Ich importer verify file: {full_path}")
        if not filetype.is_image(full_path):
            logging.debug(f"Not identified as a file, looks like: {filetype.guess(full_path)}")
            if full_path.lower().endswith(".tif") or full_path.lower().endswith(".tiff"):
                print("Tiff file misidentified as not an image, overriding auto-recognition")
            else:
                return

        filename = os.path.basename(full_path)
        if "." not in filename:
            return
        try:
            catalog_number, collection = self.get_catalog_number(filename)
        except FilenameFormatException:
            catalog_number = None
        if catalog_number is None:
            logging.debug(f"Can't find catalog number for {filename}")
            return
        logging.debug(f"Filename: {filename} Collection: {collection} catalog number: {catalog_number}")
        final_number=f"{collection}{catalog_number}"
        if final_number not in self.catalog_number_map:
            self.catalog_number_map[final_number] = [full_path]
        else:
            self.catalog_number_map[final_number].append(full_path)

    def process_catalog_number(self, catalog_number, filepath_list):
        if catalog_number is None:
            print(f"No catalog number; skipping")
            return
        print(f"Catalog number: {catalog_number}")
        sql = f"select collectionobjectid  from collectionobject where catalognumber='{catalog_number}'"
        collection_object_id = self.specify_db_connection.get_one_record(sql)
        if collection_object_id is None:
            print(f"No record found for catalog number {catalog_number}, skipping.")
            return
        self.process_id(catalog_number,filepath_list,collection_object_id,'Ichthyology',68835)



    def process_loaded_files(self):
        for catalog_number in self.catalog_number_map.keys():
            filepaths = self.catalog_number_map[catalog_number]
            filename_list = []

            for cur_filepath in filepaths:

                cur_filename = os.path.basename(cur_filepath)
                try:
                    cur_file_base, cur_file_ext = cur_filename.split(".")
                except ValueError:
                    continue
                filename_list.append([cur_filepath, cur_file_base, cur_file_ext])
            self.process_catalog_number(catalog_number, filename_list)



#         If I find a .jpg, import it.
# If I find a .tif, see if there’s already a corresponding .jpg imported. If not,
# Check the local directory to see if there’s a corresponding .jpg available. If not,
# Create a .jpg from the .tif file in a temporary directory
# Import said .jpg.
