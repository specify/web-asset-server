from attachment_utils import AttachmentUtils
import datetime
from uuid import uuid4
import os, re, sys
from image_client import ImageClient
from db_utils import DbUtils, InvalidFilenameError, DatabaseInconsistentError
import collections

TMP_JPG = "./tmp_jpg"
import logging
import subprocess
from specify_db import SpecifyDb
import shutil
from os import listdir
from os.path import isfile, join
class ConvertException(Exception):
    pass

class Importer:
    def __init__(self, db_config_class):
        self.logger = logging.getLogger('Client.importer')

        self.specify_db_connection = SpecifyDb(db_config_class)
        # self.specify_db_connection = DbUtils(
        #     db_config_class.USER,
        #     db_config_class.PASSWORD,
        #     db_config_class.SPECIFY_DATABASE_PORT,
        #     db_config_class.SPECIFY_DATABASE_HOST,
        #     db_config_class.SPECIFY_DATABASE)
        self.image_client = ImageClient()
        self.attachment_utils = AttachmentUtils(self.specify_db_connection)
        self.duplicates_file = open(f'duplicates-{self.collection_name}.txt', 'w')


    def tiff_to_jpg(self, tiff_filepath):
        basename = os.path.basename(tiff_filepath)
        if not os.path.exists(TMP_JPG):
            os.mkdir(TMP_JPG)
        else:
            shutil.rmtree(TMP_JPG)
            os.mkdir(TMP_JPG)
        file_name_no_extention, extention = basename.split('.')
        if extention != 'tif':
            self.logger.error(f"Bad filename, can't convert {tiff_filepath}")
            raise ConvertException(f"Bad filename, can't convert {tiff_filepath}")

        jpg_dest = os.path.join(TMP_JPG, file_name_no_extention + ".jpg")

        proc = subprocess.Popen(['convert', '-quality', '99', tiff_filepath, jpg_dest], stdout=subprocess.PIPE)
        output = proc.communicate(timeout=60)[0]
        onlyfiles = [f for f in listdir(TMP_JPG) if isfile(join(TMP_JPG, f))]
        if len(onlyfiles) == 0:
            raise ConvertException(f"No files producted from conversion")
        files_dict={}
        for file in onlyfiles:
            files_dict[file]=os.path.getsize(os.path.join(TMP_JPG,file))

        sort_orders = sorted(files_dict.items(), key=lambda x: x[1], reverse=True)
        top = sort_orders[0][0]
        target = os.path.join(TMP_JPG,file_name_no_extention+".jpg")
        os.rename(os.path.join(TMP_JPG,top), target)
        if len(onlyfiles) > 2:
            self.logger.info("multi-file case")

        return target,output

    def get_mime_type(self, filepath):
        mime_type = None
        if filepath.lower().endswith('.tif') or filepath.lower().endswith('.tiff'):
            mime_type = 'image/tiff'
        if filepath.lower().endswith('.jpg') or filepath.lower().endswith('.jpeg'):
            mime_type = 'image/jpeg'
        if filepath.lower().endswith('.gif'):
            mime_type = 'image/gif'
        if filepath.lower().endswith('.png'):
            mime_type = 'image/png'
        if filepath.lower().endswith('.pdf'):
            mime_type = 'application/pdf'
        return mime_type

    def import_to_specify_database(self, filepath, attach_loc, url, collection_object_id, agent_id):
        attachment_guid = uuid4()

        file_created_datetime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))

        mime_type = self.get_mime_type(filepath)

        self.attachment_utils.create_attachment(storename=attach_loc,
                                                original_filename=os.path.basename(filepath),
                                                file_created_datetime=file_created_datetime,
                                                guid=attachment_guid,
                                                image_type=mime_type,
                                                url=url,
                                                agent_id=agent_id)
        attachment_id = self.attachment_utils.get_attachment_id(attachment_guid)
        ordinal = self.attachment_utils.get_ordinal_for_collection_object_attachment(collection_object_id)
        if ordinal is None:
            ordinal = 0
        else:
            ordinal += 1
        self.attachment_utils.create_collection_object_attachment(attachment_id, collection_object_id, ordinal,
                                                                  agent_id)

    def get_first_digits_from_filepath(self, filepath, field_size=9):
        basename = os.path.basename(filepath)
        ints = re.findall(r'\d+', basename)
        if len(ints) == 0:
            raise InvalidFilenameError("Can't get barcode from filename")
        int_digits = int(ints[0])
        string_digits = f"{int_digits}"
        string_digits = string_digits.zfill(field_size)
        self.logger.debug(f"extracting digits from {filepath} to get {string_digits}")
        return string_digits

    def format_filesize(self, num, suffix="B"):
        for unit in ["", "K", "M", "G", "T"]:
            if abs(num) < 1024.0:
                return f"{num:3.1f}{unit}{suffix}"
            num /= 1024.0
        return f"{num:.1f} Yi{suffix}"

    def clean_duplicate_files(self,filepath_list):
        basename_list = [os.path.basename(filepath[0]) for filepath in filepath_list]
        basename_set = set(basename_list)
        filepath_only_list = [filepath[0] for filepath in filepath_list]
        duplicates = [item for item, count in collections.Counter(basename_list).items() if count > 1]

        for duplicate in duplicates:
            res = [item for item in filepath_only_list if duplicate in item]
            self.duplicates_file.write(f'\nDuplicate: {duplicate}\n')

            for dupe_path in res:
                size = os.path.getsize(dupe_path)
                self.logger.debug(f"dupe_path: {dupe_path}")
                self.duplicates_file.write(f"\t {self.format_filesize(size)}: {dupe_path}\n")
        clean_list = []
        for keep_name in basename_set:
            for filepath_set in filepath_list:
                if keep_name in filepath_set[0]:
                    clean_list.append(filepath_set)
        return clean_list



    def process_id(self, id, filepath_list, collection_object_id, collection, agent_id,skeleton=False):
        filepath_list = self.clean_duplicate_files(filepath_list)
        unique_filenames = {}

        for cur_filepath, cur_file_base, cur_file_ext in filepath_list:
            unique_filenames[cur_file_base] = None
        for unique_filename in unique_filenames.keys():
            self.logger.debug(f"  Processing {unique_filename} for {id}")
            jpg_found = False
            tif_found = False
            deleteme = None
            if self.image_client.check_image_db_if_already_imported(collection, unique_filename + ".jpg",exact=True):
                self.logger.info(f"  Abort; already uploaded {unique_filename}")
                continue

            for cur_filepath, cur_file_base, cur_file_ext in filepath_list:
                if cur_file_base == unique_filename:

                    if cur_file_ext == "jpg" or cur_file_ext == "jpeg":
                        jpg_found = cur_filepath
                    if cur_file_ext == "tif" or cur_file_ext == "tiff":
                        tif_found = cur_filepath
            original_full_path = jpg_found
            if not jpg_found and tif_found:
                self.logger.debug(f"  Must create jpg for {unique_filename} from {tif_found}")
                try:
                    jpg_found,output = self.tiff_to_jpg(tif_found)
                    self.logger.info(f"Converted to: {jpg_found}")
                except TimeoutError:
                    self.logger.error(f"Timeout converting {tif_found}")
                except subprocess.TimeoutExpired:
                    self.logger.error(f"Timeout converting {tif_found}")
                except ConvertException:
                    self.logger.error(f"  Conversion failure for {tif_found}; skipping.")
                    continue

                if not os.path.exists(jpg_found):
                    self.logger.error(f"  Conversion failure for {tif_found}; skipping.")
                    self.logger.debug(f"Imagemagik output: \n\n{output}\n\n")
                    continue


                deleteme = jpg_found
                original_full_path = tif_found


            if not jpg_found and tif_found:
                self.logger.debug(f"  No valid files for {unique_filename}")
                continue

            if os.path.getsize(jpg_found) < 1000:
                self.logger.info(f"This image is too small; {os.path.getsize(jpg_found)}, skipping.")
                continue
            self.logger.debug(f"  Will upload:{jpg_found} for {unique_filename}")

            try:
                if not skeleton:
                    is_redacted = self.attachment_utils.get_is_collection_object_redacted(collection_object_id)
                else:
                    is_redacted = True

                self.logger.debug(
                    f"about to import to client:- {is_redacted}, {jpg_found}, {collection}, {original_full_path}")

                url, attach_loc = self.image_client.upload_to_image_server(jpg_found,
                                                                           is_redacted,
                                                                           collection,
                                                                           original_full_path)

                self.import_to_specify_database(jpg_found, attach_loc, url, collection_object_id, agent_id)
            except Exception as e:
                self.logger.debug(
                    f"Upload failure to image server for file: \n\t{unique_filename} \n\t{jpg_found}: \n\t{original_full_path}")
                self.logger.debug(f"Exception: {e}")
            if deleteme is not None:
                os.remove(deleteme)
