import botany_importer_config

from importer import Importer
import time_utils

from uuid import uuid4
import os
import re
import logging
import filetype
from dir_tools import DirTools


# I:\botany\PLANT FAMILIES
#
# I:\botany\TYPE IMAGES
# Also, there are several sub-images with the addition of '_a' or '_b'.
# Here is an example for you to check or work with to get those secondary
# images uploaded with the first:
#
# I:\botany\TYPE IMAGES\CAS_Batch13
# CAS0410512
# CAS0410512_a

class BotanyImporter(Importer):
    def __init__(self):
        self.logger = logging.getLogger('Client.BotanyImporter')
        super().__init__(botany_importer_config,"botany")

        dir_tools = DirTools(self.build_filename_map)
        self.barcode_map = {}

        self.logger.debug("Botany import mode")

        # FILENAME = "bio_importer.bin"
        # if not os.path.exists(FILENAME):
        for cur_dir in botany_importer_config.BOTANY_SCAN_FOLDERS:
            cur_dir = os.path.join(botany_importer_config.PREFIX, botany_importer_config.BOTANY_PREFIX, cur_dir)
            print(f"Scanning: {cur_dir}")
            dir_tools.process_files_or_directories_recursive(cur_dir)

        #     outfile = open(FILENAME, 'wb')
        #     pickle.dump(self.barcode_map, outfile)
        # else:
        #     self.barcode_map = pickle.load(open(FILENAME, "rb"))
        self.process_loaded_files()

    def process_loaded_files(self):
        for barcode in self.barcode_map.keys():
            filename_list = []

            for cur_filepath in self.barcode_map[barcode]:
                filename_list.append(cur_filepath)
            self.process_barcode(barcode, filename_list)

    def process_barcode(self, barcode, filepath_list):
        if barcode is None:
            self.logger.debug(f"No barcode; skipping")
            return
        self.logger.debug(f"Barcode: {barcode}")
        collection_object_id = self.get_collectionobjectid_from_barcode(barcode)
        skeleton = False
        if collection_object_id is None:
            self.logger.debug(f"No record found for catalog number {barcode}, creating skeleton.")
            self.create_skeleton(barcode)
            skeleton = True
        #  Botany assumes that all
        filepath_list = self.clean_duplicate_files(filepath_list)

        self.process_id(filepath_list,
                         [collection_object_id],
                         95728,
                         skeleton=skeleton)

    def build_filename_map(self, full_path):
        full_path = full_path.lower()
        # self.logger.debug(f"Ich importer verify file: {full_path}")
        if not filetype.is_image(full_path):
            return

        filename = os.path.basename(full_path)
        if "." not in filename:
            self.logger.debug(f"Rejected; no . : {filename}")

            return
        matched = re.match(botany_importer_config.BOTANY_REGEX, filename.lower())
        is_match = bool(matched)
        if not is_match:
            self.logger.debug(f"Rejected; no match: {filename}")
            return
        barcode = self.get_first_digits_from_filepath(filename)
        if barcode is None:
            self.logger.debug(f"Can't find barcode for {filename}")
            return

        self.logger.debug(f"Adding filename to mappings set: {filename}   barcode: {barcode}")
        if barcode not in self.barcode_map:
            self.barcode_map[barcode] = [full_path]
        else:
            self.barcode_map[barcode].append(full_path)

    def get_collectionobjectid_from_barcode(self, barcode):
        sql = f"select collectionobjectid  from collectionobject where catalognumber={barcode}"
        return self.specify_db_connection.get_one_record(sql)

    def create_skeleton(self, barcode):
        self.logger.info(f"Creating skeleton for barcode {barcode}")
        barcode = str(barcode).zfill(9)
        cursor = self.specify_db_connection.get_cursor()
        collecting_event_guid = uuid4()
        sql = (f"""INSERT INTO collectingevent (
            TimestampCreated,
            TimestampModified,
            Version,
            GUID,
            DisciplineID
        )
        VALUES (
            '{time_utils.get_pst_time_now_string()}',
            '{time_utils.get_pst_time_now_string()}',
            0,
            '{collecting_event_guid}',
            3
        )""")
        self.logger.debug(sql)
        cursor.execute(sql)
        self.specify_db_connection.commit()

        cursor.close()

        sql = f"select CollectingEventID from collectingevent where guid='{collecting_event_guid}'"
        collecting_event_id = self.specify_db_connection.get_one_record(sql)

        cursor = self.specify_db_connection.get_cursor()
        sql = (f"""INSERT INTO collectionobject (
        TimestampCreated,
        TimestampModified,
        CollectingEventID,
        Version,
        CollectionMemberID,
        CatalogNumber,
        CatalogedDatePrecision,
        GUID,
        CollectionID,
        Date1Precision,
        InventoryDatePrecision    
        )
        VALUES ('{time_utils.get_pst_time_now_string()}',
        '{time_utils.get_pst_time_now_string()}',
        {collecting_event_id},
        0,
        4,
        '{barcode}', 
        1,
        '{uuid4()}',
        4,
        1,
        1
        )""")
        self.logger.debug(sql)
        cursor.execute(sql)
        self.specify_db_connection.commit()
        cursor.close()

    # returns None if the object is missing.
    def get_collection_object_id(self, filename):
        barcode = self.get_first_digits_from_filepath(filename)
        collection_object_id = self.get_collectionobjectid_from_barcode(barcode)
        return collection_object_id

    def import_barcode_to_specify_database(self, filepath, attach_loc, url):
        barcode = self.get_first_digits_from_filepath(filepath)
        collection_object_id = self.get_collectionobjectid_from_barcode(barcode)
        self.import_to_specify_database(filepath, attach_loc, url, collection_object_id)

    # def import_image(self, is_redacted, full_path):
    #     try:
    #         collection_object_id = self.get_collection_object_id(full_path)
    #         if collection_object_id is None:
    #             self.create_skeleton(full_path)
    #             print(f"Not importing {full_path}; Created skeleton", file=sys.stderr, flush=True)
    #             is_redacted = True
    #         else:
    #             if is_redacted != True:
    #                 is_redacted = self.attachment_utils.get_is_collection_object_redacted(collection_object_id)
    #
    #         url, attach_loc = self.image_client.upload_to_image_server(full_path, is_redacted, 'Botany')
    #         agent_id = 95728  # joe russack in botany
    #
    #         self.import_to_specify_database(full_path, attach_loc, url, collection_object_id, agent_id)
    #     except UploadFailureException:
    #         print(f"Upload failure to image server for file: {full_path}")
    #     except DatabaseInconsistentError:
    #         print(f"Database inconsistent for collection object id: {collection_object_id}, file: {full_path}",
    #               file=sys.stderr, flush=True)

    # def verify_and_import(self, full_path):
    #     if not os.path.isfile(full_path):
    #         self.logger.debug(f"Not a file: {full_path}")
    #     else:
    #         if self.file_regex_match:
    #             check_regex = os.path.basename(full_path)
    #             matched = re.match(self.file_regex_match, check_regex)
    #             is_match = bool(matched)
    #             self.logger.debug(f"Check regex {self.file_regex_match} on:{check_regex} in dir {full_path}: {is_match}")
    #             if not is_match:
    #                 return
    #
    #         if filetype.is_image(full_path):
    #             if self.image_client.check_image_db_if_already_imported('Botany', os.path.basename(full_path)):
    #                 print(f"Image {full_path} already imported, skipping..", file=sys.stderr, flush=True)
    #                 return
    #             if self.is_private:
    #                 is_redacted = True
    #             else:
    #                 is_redacted = False
    #             self.import_image(is_redacted, full_path)
    #
    #         else:
    #             self.logger.f"File found, but not image, skipping: {full_path}")
