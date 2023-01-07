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

CASIZ_FILE_LOG = "file_log.tsv"


class IzImporter(Importer):
    def __init__(self):
        logging.getLogger('PIL').setLevel(logging.ERROR)
        self.log_file = open(CASIZ_FILE_LOG, "w+")

        self.log_file.write(f"casiz\tfilename\tmethod used\tcopyright method\tcopyright\trejected\tpath on disk\n")

        self.total_file_count = 0

        self.logger = logging.getLogger('Client.IzImporter')
        self.logger.setLevel(logging.DEBUG)
        logging.getLogger('Client.DirTools').setLevel(logging.INFO)

        self.collection_name = iz_importer_config.COLLECTION_NAME
        super().__init__(iz_importer_config)

        dir_tools = DirTools(self.build_filename_map)


        self.casiz_number_map = {}
        self.path_copyright_map = {}

        self.logger.debug("IZ import mode")

        NUMBERS_FILENAME = "iz_importer_numbers.bin"
        COPYRIGHT_FILENAME = "iz_importer_copyright.bin"
        if not os.path.exists(NUMBERS_FILENAME):
            for cur_dir in iz_importer_config.IZ_SCAN_FOLDERS:
                cur_full_path = os.path.join(iz_importer_config.IMAGE_DIRECTORY_PREFIX, cur_dir)
                print(f"Scanning: {cur_full_path}")
                dir_tools.process_files_or_directories_recursive(cur_full_path)
            print("WARNING pickle disabled")
            # outfile = open(NUMBERS_FILENAME, 'wb')
            # pickle.dump(self.casiz_number_map, outfile)
            # outfile = open(COPYRIGHT_FILENAME, 'wb')
            # pickle.dump(self.path_copyright_map, outfile)

        else:
            self.casiz_number_map = pickle.load(open(NUMBERS_FILENAME, "rb"))
            self.path_copyright_map = pickle.load(open(COPYRIGHT_FILENAME, "rb"))
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
                        skeleton=skeleton,
                        copyright_map=self.path_copyright_map)

    # CASIZXXXXXX
    # CASIZ XXXXXX
    # CASIZ_XXXXXX
    # CASIZ# XXXXXX
    # CASIZ XXXXXX or CASIZ XXXXXX
    # CASIZ XXXXXX or XXXXXX
    # same as above but with "and" not "or"
    # same as above but >2 numbers in file name
    # other characters may precede "CASIZ"
    # CAT or other characters between CASIZ and # (i.e. CASIZ_CAT_XXXXX)
    # see above for Label scan files, which lack the CASIZ acronym

    def log_file_status(self, id=None, filename=None, path=None, method=None, rejected=None, copyright_method=None,
                        copyright=None):
        if rejected is None:
            rejected = "-"
        if method is None:
            method = "-"
        if copyright is None:
            copyright = "-"
        if id is None or rejected is True:
            id = "-"
        print(f"Logged: {id} copyright method: {copyright_method} copyright: \'{copyright}\' rejected:{rejected}")
        self.log_file.write(f"{id}\t{filename}\t{method}\t{copyright_method}\t{copyright}\t{rejected}\t{path}\n")
        return

    # Hangs on some files, don't know why, needs to be killed
    @timeout(20, os.strerror(errno.ETIMEDOUT))
    def exif_data_extrator(self, filepath):
        print(f"        Extracting exif: {filepath}")
        return Image.open(filepath).getexif()

    def extract_casiz(self, candidate_string):
        ints = re.findall(iz_importer_config.CASIZ_MATCH, candidate_string)
        if len(ints) > 0:
            return ints[0][1]
        return None

    def extract_copyright(self, copyright_string):
        copyright = None
        if '©' in copyright_string:
            copyright = copyright_string.split('©')[-1]
        if 'copyright' in copyright_string:
            copyright = copyright_string.split('copyright')[-1]
        if copyright is not None:
            copyright = copyright.strip()
            copyright = os.path.splitext(copyright)[0]
        return copyright

    def build_filename_map(self, full_path):
        method = None
        orig_case_directory=os.path.dirname(full_path)
        orig_case_filename=os.path.basename(full_path)
        full_path = full_path.lower()
        filename = os.path.basename(full_path)
        directory = os.path.dirname(full_path)


        matched = re.match(iz_importer_config.FILENAME_MATCH, filename)
        match_filename = bool(matched)

        # matched = re.match(iz_importer_config.FILENAME_COMPLEX_MATCH, filename)
        # filename_complex_match = bool(matched)

        # matched = re.match(iz_importer_config.FILENAME_EXACT_MATCH, filename)
        # filename_exact_match = bool(matched)

        matched = re.match(iz_importer_config.FILENAME_OR_MATCH, filename)
        filename_or_match = bool(matched)

        matched = re.match(iz_importer_config.FILENAME_AND_MATCH, filename)
        filename_and_match = bool(matched)

        # # If there's more than one number sequence, we don't know which
        # # is the ID, so reject unless it's an exact match
        # # of the form casiz[- _]number
        # number_sequence_count =len(re.findall('[0-9]{4,}', filename))
        # if number_sequence_count > 1 and not match_filename:
        #     print(f"Rejected - too many possible IDs: {filename}  -  {full_path}")
        #     self.log_file_status(filename=filename, path=full_path, rejected="No ID found")
        #     return
        if filename_or_match:
            print(f"Rejected - or condition is ambiguous: {filename}  -  {full_path}")
            self.log_file_status(filename=filename, path=full_path, rejected="or condition")
            return

        if filename_and_match:
            print(f"Rejected - and condition is not handled: {filename}  -  {full_path}")
            self.log_file_status(filename=filename, path=full_path, rejected="and condition")
            return

        # if match_filename is False and filename_exact_match is True:
        #     match_filename = True

        casiz_number = None
        #  check directory path to see if the dir has the ID
        directories = directory.split('/')
        match_directory = None
        for cur_directory in reversed(directories):
            matched = re.search(iz_importer_config.IZ_DIRECTORY_REGEX, cur_directory)
            match_directory = bool(matched)
            if match_directory:
                directory = cur_directory
                break

        if not (match_filename or match_directory):
            self.log_file_status(filename=filename, path=full_path, rejected="no match")
            return
        if match_filename:
            casiz_number = self.extract_casiz(filename)
            method = "filename"

        else: # match_directory:
            casiz_number = self.extract_casiz(directory)
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


        except Exception as e:
            self.logger.error(f"Unable to process image for exif: {e}\n\t{full_path}")
            print(f"Unable to process image for exif: {e}\n\t{full_path}")

        if casiz_number is None:
            if "ImageDescription" in deocded_exif_data.keys():
                image_description = deocded_exif_data['ImageDescription']
                ints = re.findall(r'\d+', image_description)
                if len(ints) == 0:
                    self.logger.debug(f" Can't find any id number in the image description: {image_description}")
                else:
                    if len(ints[0]) >= iz_importer_config.MINIMUM_ID_DIGITS:
                        casiz_number = int(ints[0])
                        method = "exif"

        if casiz_number is None:
            reject_string = "Rejected: Can't find casiz_number for {filename}  -  {full_path}. exif data: {exif_data}"
            self.logger.debug(reject_string)

            self.log_file_status(filename=filename, path=full_path, rejected="No ID found")
            print(reject_string)
            return

        self.logger.debug(f"Adding filename to mappings set: {filename}   casiz_number: {casiz_number}")
        print(f"Accepted: {casiz_number}:'{filename}'  ----- '{full_path}'")
        self.total_file_count += 1
        # ================= copyright =================
        copyright = None
        copyright_method = None
        copyright_directory = self.extract_copyright(orig_case_directory)
        if copyright_directory is not None:
            print('Copyright symbol detected in directory')
            copyright = f'{copyright_directory}'
            copyright_method = 'directory'
        copyright_filename = self.extract_copyright(orig_case_filename)
        if copyright_filename is not None:
            print('Copyright symbol detected in filename')
            copyright = f'{copyright_filename}'
            copyright_method = 'filename'

        if 'Copyright' in deocded_exif_data.keys():
            copyright = deocded_exif_data['Copyright']
            if copyright.startswith('Â'):
                copyright = copyright[1:]
            copyright = copyright
            copyright_method = 'exif'

        self.path_copyright_map[full_path] = copyright
        # ================= end copyright =================

        self.log_file_status(filename=filename, path=full_path, method=method, id=casiz_number,
                             copyright_method=copyright_method, copyright=copyright)

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
