import iz_importer_config

from importer import Importer
from timeout import timeout
import errno

import os
import re
import logging
from dir_tools import DirTools
from PIL import Image
import pickle
import func_timeout

MINIMUM_ID_DIGITS=5

CASIZ_FILE_LOG = "file_log.tsv"


class IzImporter(Importer):
    def __init__(self):
        logging.getLogger('PIL').setLevel(logging.ERROR)
        self.log_file = open(CASIZ_FILE_LOG, "w+")
        self.total_file_count=0


        self.logger = logging.getLogger('Client.IzImporter')
        self.logger.setLevel(logging.DEBUG)
        logging.getLogger('Client.DirTools').setLevel(logging.INFO)

        self.collection_name = iz_importer_config.COLLECTION_NAME
        super().__init__(iz_importer_config)

        dir_tools = DirTools(self.build_filename_map)
        # logging.getLogger('Client.DirTools').setLevel(logging.INFO)

        # dir_tools.logger.setLevel(logging.DEBUG)

        self.casiz_number_map = {}

        self.logger.debug("IZ import mode")

        FILENAME = "iz_importer.bin"
        if not os.path.exists(FILENAME):
            for cur_dir in iz_importer_config.IZ_SCAN_FOLDERS:
                cur_full_path = os.path.join(iz_importer_config.IMAGE_DIRECTORY_PREFIX, cur_dir)
                print(f"Scanning: {cur_full_path}")
                dir_tools.process_files_or_directories_recursive(cur_full_path)

            outfile = open(FILENAME, 'wb')
            pickle.dump(self.casiz_number_map, outfile)
        else:
            self.casiz_number_map = pickle.load(open(FILENAME, "rb"))
        print("Starting to process loaded files...")
        self.process_loaded_files()

    def process_loaded_files(self):
        for casiz_number in self.casiz_number_map.keys():
            filepaths = self.casiz_number_map[casiz_number]
            filename_list = []

            for cur_filepath in filepaths:

                cur_filename = os.path.basename(cur_filepath)
                try:
                    cur_file_base, cur_file_ext = cur_filename.split(".")
                except ValueError:
                    continue
                filename_list.append([cur_filepath, cur_file_base, cur_file_ext])
            self.process_casiz_number(casiz_number, filename_list)

    def process_casiz_number(self, casiz_number, filepath_list):
        if casiz_number is None:
            self.logger.debug(f"No casiz_number; skipping")
            return
        self.logger.debug(f"casiz_number: {casiz_number}")
        collection_object_id = self.get_collectionobjectid_from_casiz_number(casiz_number)
        skeleton = False
        if collection_object_id is None:
            self.logger.debug(f"No record found for catalog number {casiz_number}, skeleton creation disabled.")

            # self.create_skeleton(casiz_number)
            # skeleton = True
            return

        self.process_id(casiz_number,
                        filepath_list,
                        collection_object_id,
                        iz_importer_config.COLLECTION_NAME,
                        26280,
                        skeleton=skeleton)

    def log_file_status(self, id=None, filename=None, path=None, method=None, rejected=None, copyright=None):
        if rejected is None:
            rejected = "-"
        if method is None:
            method = "-"
        if copyright is None:
            copyright = "-"
        if id is None or rejected is True:
            id = "-"

        self.log_file.write(f"{id}\t{filename}\t{method}\t{copyright}\t{rejected}\t{path}\n")
        return

    # Hangs on some files, don't know why, needs to be killed
    @timeout(10, os.strerror(errno.ETIMEDOUT))
    def exif_data_extrator(self,filepath):
        return Image.open(filepath).getexif()

    def build_filename_map(self, full_path):
        method = None
        full_path = full_path.lower()
        filename = os.path.basename(full_path)

        matched = re.match(iz_importer_config.FILENAME_SIMPLE_MATCH, filename)
        filename_simple_match = bool(matched)

        matched = re.match(iz_importer_config.FILENAME_COMPLEX_MATCH, filename)
        filename_complex_match = bool(matched)
        casiz_number = None
        #  check directory path to see if the dir has the ID
        directory = os.path.dirname(full_path)
        directories = directory.split('/')
        match_directory = None
        for cur_directory in reversed(directories):
            matched = re.search(iz_importer_config.IZ_DIRECRTORY_REGEX, cur_directory)
            match_directory = bool(matched)
            if match_directory:
                directory = cur_directory
                break

        if not filename_simple_match:
            print(f"Rejected 4: {filename}  -  {full_path}")
            self.logger.debug(f"Rejected; not image: {filename}  -  {full_path}")

            # self.log_file_status(None,"Not image")
            return
        if filename_complex_match:
            casiz_number = self.get_first_digits_from_filepath(filename, field_size=0)
            method = "filename"
        if casiz_number is None and match_directory:
            directory = os.path.basename(directory)
            ints = re.findall(r'\d+', directory)
            if len(ints) > 0:
                if len(ints[-1]) >= MINIMUM_ID_DIGITS:

                    casiz_number = int(ints[-1])
                    method = "directory"

        deocded_exif_data = {}
        exif_data = None
        try:
            # func = Image.open
            # exif_data_raw = func_timeout(10, Image.open, args=(full_path))
            # # exif_data = Image.open(full_path).getexif()
            # exif_data = func(full_path).getexif()
            #
            # # exif_data = exif_data_raw.getexif()
            exif_data = self.exif_data_extrator(full_path)

            if exif_data is not None:
                # print("processing exif data")
                for key, value in exif_data.items():
                    # print(f"Processing {key}:{value}")
                    if key in iz_importer_config.EXIF_DECODER_RING.keys():
                        # print(f"  {iz_importer_config.EXIF_DECODER_RING[key]}: {value}")
                        deocded_exif_data[iz_importer_config.EXIF_DECODER_RING[key]] = value

        except errno.ETIMEDOUT as e:
            print(f"TIMEOUT ------------------: {e}")
        except Exception as e:
            self.logger.error(f"Unable to process image for exif: {e}\n\t{full_path}")
            print(f"Unable to process image for exif: {e}\n\t{full_path}")

        if filename_simple_match and casiz_number is None:
            if "ImageDescription" in deocded_exif_data.keys():
                image_description = deocded_exif_data['ImageDescription']
                ints = re.findall(r'\d+', image_description)
                if len(ints) == 0:
                    self.logger.debug(f" Can't find any id number in the image description: {image_description}")
                else:
                    if len(ints[0]) >= MINIMUM_ID_DIGITS:
                        casiz_number = int(ints[0])
                        method = "exif"

        if casiz_number is None:
            self.logger.debug(
                f"Rejected: Can't find casiz_number for {filename}  -  {full_path}. exif data: {exif_data}")
            self.log_file_status(filename=filename, path=full_path, rejected="No ID found")
            return

        self.logger.debug(f"Adding filename to mappings set: {filename}   casiz_number: {casiz_number}")
        print(f"Accepted: {casiz_number}:'{filename}'  ----- '{full_path}'")
        self.total_file_count += 1


        if 'Copyright' in deocded_exif_data.keys():
            copyright= deocded_exif_data['Copyright']
        else:
            copyright = None
        self.log_file_status(filename=filename, path=full_path, method=method, id=casiz_number,
                             copyright=copyright)

        if casiz_number not in self.casiz_number_map:
            self.casiz_number_map[casiz_number] = [full_path]
        else:
            self.casiz_number_map[casiz_number].append(full_path)

    def get_collectionobjectid_from_casiz_number(self, casiz_number):
        sql = f"select collectionobjectid  from collectionobject where catalognumber={casiz_number}"
        return self.specify_db_connection.get_one_record(sql)


    # returns None if the object is missing.
    def get_collection_object_id(self, filename):
        casiz_number = self.get_first_digits_from_filepath(filename)
        collection_object_id = self.get_collectionobjectid_from_casiz_number(casiz_number)
        return collection_object_id

    def import_casiz_number_to_specify_database(self, filepath, attach_loc, url):
        casiz_number = self.get_first_digits_from_filepath(filepath)
        collection_object_id = self.get_collectionobjectid_from_casiz_number(casiz_number)
        self.import_to_specify_database(filepath, attach_loc, url, collection_object_id)
