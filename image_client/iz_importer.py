import sys

import iz_importer_config

from importer import Importer

import os
import re
import logging
from dir_tools import DirTools
from exif_tools import ExifTools
import traceback

CASIZ_FILE_LOG = "file_log.tsv"


#  EXIF takes first priority Directory takes second. File name takes 3rd.


class IzImporter(Importer):
    class item_mapping:
        def __init__(self):
            self.casiz_numbers = []

    def __init__(self):
        logging.getLogger('PIL').setLevel(logging.ERROR)
        self.AGENT_ID = 26280
        self.log_file = open(CASIZ_FILE_LOG, "w+")
        self.item_mappings = []
        self.log_file.write(f"casiz\tfilename\tCASIZ method\tcopyright method\tcopyright\trejected\tpath on disk\n")

        self.logger = logging.getLogger('Client.IzImporter')
        self.logger.setLevel(logging.DEBUG)
        logging.getLogger('Client.DirTools').setLevel(logging.INFO)

        self.collection_name = iz_importer_config.COLLECTION_NAME
        super().__init__(iz_importer_config, "Invertebrate Zoology")

        dir_tools = DirTools(self.build_filename_map)

        self.casiz_filepath_map = {}
        self.path_copyright_map = {}

        self.logger.debug("IZ import mode")

        # aux label files - simple regex
        self.cur_conjunction_match = None
        self.cur_filename_match = iz_importer_config.NUMBER_ONLY_MATCH
        self.cur_directory_match = None
        self.cur_directory_conjunction_match = None

        self.cur_casiz_match = iz_importer_config.CASIZ_NUMBER
        self.cur_extract_casiz = self.extract_casiz_single
        for cur_dir in iz_importer_config.IZ_AUX_SCAN_FOLDERS:
            cur_full_path = os.path.join(cur_dir)
            print(f"Scanning: {cur_full_path}")
            dir_tools.process_files_or_directories_recursive(cur_full_path)

        print("Starting to process loaded label files...")
        self.process_loaded_files()

        self.cur_conjunction_match = iz_importer_config.FILENAME_CONJUNCTION_MATCH + iz_importer_config.IMAGE_SUFFIX
        self.cur_filename_match = iz_importer_config.FILENAME_MATCH + iz_importer_config.IMAGE_SUFFIX
        self.cur_directory_match = iz_importer_config.FILENAME_MATCH
        self.cur_directory_conjunction_match = iz_importer_config.FILENAME_CONJUNCTION_MATCH

        self.cur_casiz_match = iz_importer_config.CASIZ_MATCH
        self.cur_extract_casiz = self.extract_casiz

        for cur_dir in iz_importer_config.IZ_CORE_SCAN_FOLDERS:
            cur_full_path = os.path.join(cur_dir)
            print(f"Scanning: {cur_full_path}")
            dir_tools.process_files_or_directories_recursive(cur_full_path)

        print("Starting to process loaded core files...")
        self.process_loaded_files()

    def process_loaded_files(self):
        print("PROCESSING TEMPORARILY DISABLED FOR TESTING JOE JOE JOE")
        return
        for casiz_number in self.casiz_filepath_map.keys():
            filepaths = self.casiz_filepath_map[casiz_number]
            filepath_list = []
            #  redundant from an old cleaning operation but harmless for now
            for cur_filepath in filepaths:
                filepath_list.append(cur_filepath)

            self.process_casiz_number(casiz_number, filepath_list)

    def process_casiz_number(self, casiz_number, filepath_list):
        self.logger.debug(f"casiz_numbers: {casiz_number}")
        sql = f"select collectionobjectid  from collectionobject where catalognumber={casiz_number}"
        collection_object_id = self.specify_db_connection.get_one_record(sql)
        if collection_object_id is None:
            print(f"No record found for casiz_number {casiz_number}, skipping.")
            return
        # remove the subset of already-seen filepaths from the filepath import list.
        # "is this in specify attached to this casiz" query
        filepath_list = self.remove_specify_imported_and_id_linked_from_path(filepath_list, collection_object_id)

        # now, check if the attachment is already in there (AND case):
        for cur_filepath in filepath_list:
            attachment_id = self.attachment_utils.get_attachmentid_from_filepath(cur_filepath)

            if attachment_id is not None:
                # if so, link attachment to this COID:
                self.connect_existing_attachment_to_collection_object_id(attachment_id,
                                                                         collection_object_id,
                                                                         self.AGENT_ID)
            else:
                # If not:
                self.import_to_imagedb_and_specify([cur_filepath],
                                                   collection_object_id,
                                                   self.AGENT_ID,
                                                   copyright_filepath_map=self.path_copyright_map,
                                                   force_redacted=True)

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

    def extract_casiz_single(self, candidate_string):
        ints = re.findall(iz_importer_config.CASIZ_NUMBER, candidate_string)
        if len(ints) > 0:
            return ints[0]
        return None

    def extract_casiz(self, candidate_string):
        ints = re.findall(iz_importer_config.CASIZ_MATCH, candidate_string)
        if len(ints) > 0:
            return ints[0][1]
        return None

    def extract_copyright_from_string(self, copyright_string):
        copyright = None
        if '©' in copyright_string:
            copyright = copyright_string.split('©')[-1]
        if 'copyright' in copyright_string:
            copyright = copyright_string.split('copyright')[-1]
        if copyright is not None:
            copyright = copyright.strip()
            copyright = os.path.splitext(copyright)[0]
        return copyright

    def attempt_exif_extraction(self, full_path):
        try:
            return ExifTools(full_path)
        except Exception as e:
            print(f"Exception: {e}")
            traceback.print_exc()

            return None

    def attempt_exif_match(self, full_path):
        if self.exif_tools is None:
            return False
        if self.exif_tools.casiz_number is not None:
            self.casiz_numbers = [self.exif_tools.casiz_number]
            return True
        return False

    def attempt_directory_match(self, full_path):
        directory = os.path.dirname(full_path)

        directories = directory.split('/')

        for cur_directory in reversed(directories):

            if self.cur_directory_conjunction_match is not None:
                result = re.search(self.cur_directory_conjunction_match, cur_directory)
                if result:
                    found_substring = result.groups()[0]
                    self.casiz_numbers = list(set([int(num) for num in re.findall(r'\b\d+\b', found_substring)]))
                    return True
            if self.cur_directory_match is not None:
                if re.search(self.cur_directory_match, cur_directory):
                    self.casiz_numbers = [self.cur_extract_casiz(directory)]
                    return True
        return False

    def attempt_filename_match(self, full_path):
        filename = os.path.basename(full_path)

        if re.search(self.cur_filename_match, filename):
            self.casiz_numbers = [self.cur_extract_casiz(filename)]
            return True
        if self.cur_conjunction_match is not None:
            if re.search(self.cur_conjunction_match, filename):
                p = re.compile(self.cur_conjunction_match)
                result = p.search(filename)
                found_substring = result.groups()[0]
                self.casiz_numbers = list(set([int(num) for num in re.findall(r'\b\d+\b', found_substring)]))
                print(f"Matched conjunction on {filename}. IDs: {self.casiz_numbers}")
                return True
        return False

    def attempt_directory_copyright_extraction(self, directory_orig_case):
        directories = directory_orig_case.split('/')

        for cur_directory in reversed(directories):
            copyright = self.extract_copyright_from_string(cur_directory)
            if copyright is not None:
                self.copyright = copyright
                return True
        return False

    def extract_copyright_from_file(self, orig_case_full_path):
        orig_case_directory = os.path.dirname(orig_case_full_path)
        orig_case_filename = os.path.basename(orig_case_full_path)
        self.copyright = None
        copyright_method = None
        if self.exif_tools:
            if self.exif_tools.copyright is not None:
                self.copyright = self.exif_tools.copyright
                return 'exif'
        if self.attempt_directory_copyright_extraction(orig_case_directory):
            return 'directory'

        filename_copyright = self.extract_copyright_from_string(orig_case_filename)
        if filename_copyright is not None:
            copyright_method = 'filename'
            self.copyright = filename_copyright
            return 'filename'

        return None

    def check_already_attached(self, full_path):
        attachment_id = self.attachment_utils.get_attachmentid_from_filepath(full_path)
        if attachment_id is not None:
            return True
        return False

    def exclude_by_extension(self,full_path):
        extension = full_path.rsplit('.', 1)[-1]
        if extension in iz_importer_config.EXCLUDE_EXTENSIONS:
            return True
        else:
            return False

    def check_already_in_image_db(self, full_path):


        if self.image_client.check_image_db_if_filepath_imported(self.collection_name,
                                                                 full_path,
                                                                 exact=True):
            return True
        return False

    def build_filename_map(self, full_path):
        orig_case_full_path = full_path
        full_path = full_path.lower()
        if self.exclude_by_extension(full_path):
            print(f"Will not import, exluded extension: {full_path}")
            self.log_file_status(filename=os.path.basename(full_path),
                                 path=full_path,
                                 rejected="forbidden extension")
            return False

        if self.check_already_attached(full_path):
            print(f"Already imported {orig_case_full_path}")
            return False


        # if self.check_already_in_image_db(full_path):
        #     print(f"Already in image db {orig_case_full_path}")
        #     return False

        self.exif_tools = self.attempt_exif_extraction(full_path)
        self.casiz_numbers = None
        if self.attempt_exif_match(full_path):
            casiz_source = 'EXIF'
        else:
            if self.attempt_directory_match(full_path):
                casiz_source = 'Directory'
            else:
                if self.attempt_filename_match(full_path):
                    casiz_source = 'Filename'
                else:
                    self.log_file_status(filename=os.path.basename(full_path),
                                         path=full_path,
                                         rejected="no casiz match for exif, filename, or directory.")
                    return False

        # -------- copyright --------
        copyright_method = self.extract_copyright_from_file(orig_case_full_path)

        if self.copyright:
            self.path_copyright_map[full_path] = self.copyright

        for cur_casiz_number in self.casiz_numbers:
            if cur_casiz_number not in self.casiz_filepath_map:
                self.casiz_filepath_map[cur_casiz_number] = [full_path]
            else:
                self.casiz_filepath_map[cur_casiz_number].append(full_path)

        self.log_file_status(filename=os.path.basename(orig_case_full_path),
                             path=orig_case_full_path,
                             method=casiz_source,
                             id=self.casiz_numbers,
                             copyright_method=copyright_method,
                             copyright=self.copyright)
        return True

    def get_collectionobjectid_from_casiz_number(self, casiz_number):
        sql = f"select collectionobjectid  from collectionobject where catalognumber={casiz_number}"
        return self.specify_db_connection.get_one_record(sql)
