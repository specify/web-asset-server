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

CASIZ_FILE_LOG = "file_log.tsv"

#  EXIF takes first priority Directory takes second. File name takes 3rd.

'''
Just to confirm the plan, will you also be writing the info to EXIF image fields and Specify Attachment 
fields as we'd discussed? These are templates I'd saved on Pegasus here: 
I:\izg\IZ\for Joe_modify metadata_all Hearst-VIP-CRRF, for example see the template pasted below.
Thanks! 
[IPTC Core field (metadata): text to be entered]
Copyright Status:  Copyrighted
Copyright Notice:  © Terrence M. Gosliner licensed under Creative Commons BY-NC-SA
Creator: Terrence M. Gosliner
Credit Line: Terrence M. Gosliner, California Academy of Sciences
Rights Usage Terms: Creative Commons Attribution-NonCommercial-ShareAlike - CC BY-NC-SA
Title: CASIZ number (if feasible)
File Properties:Notes:  False
File Properties:Label:  StillImage
Attributes:Label:  Live

[Specify Attachments field data to be entered]
CopyrightHolder: © Terrence M. Gosliner licensed under Creative Commons BY-NC-SA
Creator: Terrence M. Gosliner
Credit: Terrence M. Gosliner, California Academy of Sciences
License: Creative Commons Attribution-NonCommercial-ShareAlike - CC BY-NC-SA
Title: CASIZ number
NotPublic: False
Type: StillImage
subType: Live 
'''


class IzImporter(Importer):
    class item_mapping:
        def __init__(self):
            self.casiz_numbers = []

    def __init__(self):
        logging.getLogger('PIL').setLevel(logging.ERROR)
        self.log_file = open(CASIZ_FILE_LOG, "w+")
        self.item_mappings = []
        self.log_file.write(f"casiz\tfilename\tCASIZ method\tcopyright method\tcopyright\trejected\tpath on disk\n")

        self.total_file_count = 0

        self.logger = logging.getLogger('Client.IzImporter')
        self.logger.setLevel(logging.DEBUG)
        logging.getLogger('Client.DirTools').setLevel(logging.INFO)

        self.collection_name = iz_importer_config.COLLECTION_NAME
        super().__init__(iz_importer_config, "Invertebrate Zoology")

        dir_tools = DirTools(self.build_filename_map)

        self.casiz_filepath_map = {}
        self.filepath_casiz_map = {}

        self.path_copyright_map = {}

        self.logger.debug("IZ import mode")

        casiz_filepath_map_filename = "iz_importer_casiz_filepath.bin"
        filepath_casiz_map_filename = "iz_importer_filepath_casiz.bin"

        COPYRIGHT_FILENAME = "iz_importer_copyright.bin"
        if not os.path.exists(casiz_filepath_map_filename):
            for cur_dir in iz_importer_config.IZ_SCAN_FOLDERS:
                cur_full_path = os.path.join(iz_importer_config.IMAGE_DIRECTORY_PREFIX, cur_dir)
                print(f"Scanning: {cur_full_path}")
                dir_tools.process_files_or_directories_recursive(cur_full_path)
            # print("WARNING pickle disabled")
            outfile = open(casiz_filepath_map_filename, 'wb')
            pickle.dump(self.casiz_filepath_map, outfile)
            outfile = open(filepath_casiz_map_filename, 'wb')
            pickle.dump(self.filepath_casiz_map, outfile)
            outfile = open(COPYRIGHT_FILENAME, 'wb')
            pickle.dump(self.path_copyright_map, outfile)

        else:
            self.filepath_casiz_map = pickle.load(open(filepath_casiz_map_filename, "rb"))
            self.casiz_filepath_map = pickle.load(open(casiz_filepath_map_filename, "rb"))
            self.path_copyright_map = pickle.load(open(COPYRIGHT_FILENAME, "rb"))
        print("Starting to process loaded files...")
        self.process_loaded_files()

    def process_loaded_files(self):
        # joe this is fubar; we can no longer use this method because
        # we can have a set of files map to a set of casiz numbers
        for casiz_number in self.casiz_filepath_map.keys():
            filepaths = self.casiz_filepath_map[casiz_number]
            filepath_list = []

            for cur_filepath in filepaths:

                cur_filename = os.path.basename(cur_filepath)
                try:
                    cur_file_base, cur_file_ext = cur_filename.split(".")
                except ValueError:
                    continue
                filepath_list.append(cur_filepath)

            self.process_casiz_number(casiz_number, filepath_list)

    def process_casiz_number(self, casiz_number, filepath_list):
        self.logger.debug(f"casiz_numbers: {casiz_number}")
        sql = f"select collectionobjectid  from collectionobject where catalognumber={casiz_number}"
        collection_object_id = self.specify_db_connection.get_one_record(sql)
        if collection_object_id is None:
            print(f"No record found for casiz_number {casiz_number}, skipping.")
            return
        filepath_list = self.remove_imported_filepaths_from_list(filepath_list)
        self.import_to_imagedb_and_specify(filepath_list, collection_object_id, 26280,copyright_map=self.path_copyright_map)


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

    def log_file_status(self,
                        id=None,
                        filename=None,
                        path=None,
                        method=None,
                        rejected=None,
                        copyright_method=None,
                        copyright=None,
                        conjunction=None):
        if rejected is None:
            rejected = "-"
        if method is None:
            method = "-"
        if copyright is None:
            copyright = "-"
        if id is None or rejected is True:
            id = "-"
        if conjunction:
            id = conjunction
        print(
            f"Logged: {id} copyright method: {copyright_method} copyright: \'{copyright}\' rejected:{rejected} filename: {filename}")
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

    def get_decoded_exif_data(self, full_path):
        decoded_exif_data = {}

        try:
            exif_data = self.exif_data_extrator(full_path)

            if exif_data is not None:
                # print("processing exif data")
                for key, value in exif_data.items():
                    # print(f"Processing {key}:{value}")
                    if key in iz_importer_config.EXIF_DECODER_RING.keys():
                        print(f"  {iz_importer_config.EXIF_DECODER_RING[key]}: {value}")
                        decoded_exif_data[iz_importer_config.EXIF_DECODER_RING[key]] = value
        except Exception as e:
            pass

        return decoded_exif_data

    def get_casiz_from_decoded_exif_data(self, deocded_exif_data):
        if "ImageDescription" in deocded_exif_data.keys():
            image_description = deocded_exif_data['ImageDescription']
            ints = re.findall(r'\d+', image_description)
            if len(ints) == 0:
                self.logger.debug(f" Can't find any id number in the image description: {image_description}")
            else:
                if len(ints[0]) >= iz_importer_config.MINIMUM_ID_DIGITS:
                    casiz_number = int(ints[0])
                    return casiz_number
        return None

    def build_filename_map(self, full_path):
        method = None
        orig_case_directory = os.path.dirname(full_path)
        orig_case_filename = os.path.basename(full_path)
        full_path = full_path.lower()
        filename = os.path.basename(full_path)
        directory = os.path.dirname(full_path)

        if not re.search(iz_importer_config.IMAGE_SUFFIX, filename):
            self.log_file_status(filename=filename, path=full_path, rejected="not an image file")
            return

        matched = re.match(iz_importer_config.FILENAME_MATCH, filename)
        match_filename = bool(matched)

        matched = re.match(iz_importer_config.FILENAME_CONJUNCTION_MATCH, filename)
        filename_conjunction_match = bool(matched)

        #  check directory path to see if the dir has the ID
        directories = directory.split('/')
        match_directory = None
        for cur_directory in reversed(directories):
            matched = re.search(iz_importer_config.IZ_DIRECTORY_REGEX, cur_directory)
            match_directory = bool(matched)
            if " and " in filename or " or " in cur_directory:
                print("And found - directory joe check stop here")
            if match_directory:
                directory = cur_directory
                break

        casiz_number = None
        decoded_exif_data = self.get_decoded_exif_data(full_path)
        casiz_from_exif = self.get_casiz_from_decoded_exif_data(decoded_exif_data)

        if not (match_filename or match_directory or casiz_from_exif):
            self.log_file_status(filename=filename, path=full_path, rejected="no match")
            return

        if casiz_from_exif is not None:
            casiz_number = casiz_from_exif
            method = "exif"
        elif match_directory:
            casiz_number = self.extract_casiz(directory)
            method = "directory"
        elif match_filename:
            casiz_number = self.extract_casiz(filename)
            method = "filename"

        if not re.search(iz_importer_config.IMAGE_SUFFIX, filename):
            self.log_file_status(filename=filename, path=full_path, rejected="not an image file")
            return

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
        copyright_filename = self.extract_copyright(orig_case_filename)

        if 'Copyright' in decoded_exif_data.keys():
            copyright = decoded_exif_data['Copyright']
            if copyright.startswith('Â'):
                copyright = copyright[1:]
            copyright = copyright
            copyright_method = 'exif'
        elif copyright_directory is not None:
            print('Copyright symbol detected in directory')
            copyright = f'{copyright_directory}'
            copyright_method = 'directory'
        elif copyright_filename is not None:
            print('Copyright symbol detected in filename')
            copyright = f'{copyright_filename}'
            copyright_method = 'filename'

        self.path_copyright_map[full_path] = copyright
        # ================= end copyright =================

        self.log_file_status(filename=filename,
                             path=full_path,
                             method=method,
                             id=casiz_number,
                             copyright_method=copyright_method,
                             copyright=copyright)

        if filename_conjunction_match:
            p = re.compile(iz_importer_config.FILENAME_CONJUNCTION_MATCH)
            result = p.search(filename)
            casiz_numbers = [int(num) for num in re.findall(r'\b\d+\b', result.group(0))]
            print(f"Matched conjunction on {filename}. IDs: {casiz_numbers[0]} and {casiz_numbers[1]}")
            self.log_file_status(filename=filename, path=full_path, conjunction=f"{casiz_number[0]},{casiz_number[1]}",
                                 rejected=False)
        else:
            casiz_numbers = [casiz_number]

        for cur_casiz_number in casiz_numbers:
            if cur_casiz_number not in self.casiz_filepath_map:
                self.casiz_filepath_map[cur_casiz_number] = [full_path]
            else:
                self.casiz_filepath_map[cur_casiz_number].append(full_path)
            if full_path not in self.filepath_casiz_map:
                self.filepath_casiz_map[full_path] = [cur_casiz_number]
            else:
                self.filepath_casiz_map[full_path].append(cur_casiz_number)

    def get_collectionobjectid_from_casiz_number(self, casiz_number):
        sql = f"select collectionobjectid  from collectionobject where catalognumber={casiz_number}"
        return self.specify_db_connection.get_one_record(sql)




