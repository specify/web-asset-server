from attachment_utils import AttachmentUtils
import datetime
from uuid import uuid4
import os, re, sys
from image_client import ImageClient
from db_utils import DbUtils, InvalidFilenameError, DatabaseInconsistentError
import collections
import filetype

TMP_JPG = "./tmp_jpg"
import logging
import subprocess
from specify_db import SpecifyDb
import shutil
from os import listdir
from os.path import isfile, join


class ConvertException(Exception):
    pass


# class FilePath():
#     def __init__(self, filepath):
#         cur_filename = os.path.basename(filepath)
#
#         cur_file_base, cur_file_ext = cur_filename.split(".")
#
#         self.full_path = filepath
#         self.filename = cur_filename
#         self.basename = cur_file_base
#         self.ext = cur_file_ext
#
#     def __str__(self):
#         return self.full_path


class Importer:
    def __init__(self, db_config_class, collection_name):
        self.logger = logging.getLogger('Client.importer')
        self.collection_name = collection_name
        self.specify_db_connection = SpecifyDb(db_config_class)
        self.image_client = ImageClient()
        self.attachment_utils = AttachmentUtils(self.specify_db_connection)
        self.duplicates_file = open(f'duplicates-{self.collection_name}.txt', 'w')

    def split_filepath(self,filepath):
        cur_filename = os.path.basename(filepath)
        cur_file_ext = cur_filename.split(".")[1]
        return cur_filename, cur_file_ext

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
        files_dict = {}
        for file in onlyfiles:
            files_dict[file] = os.path.getsize(os.path.join(TMP_JPG, file))

        sort_orders = sorted(files_dict.items(), key=lambda x: x[1], reverse=True)
        top = sort_orders[0][0]
        target = os.path.join(TMP_JPG, file_name_no_extention + ".jpg")
        os.rename(os.path.join(TMP_JPG, top), target)
        if len(onlyfiles) > 2:
            self.logger.info("multi-file case")

        return target, output

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

    def import_to_specify_database(self, filepath, attach_loc, url, collection_object_id, agent_id, copyright=None):
        attachment_guid = uuid4()

        file_created_datetime = datetime.datetime.fromtimestamp(os.path.getmtime(filepath))

        mime_type = self.get_mime_type(filepath)

        self.attachment_utils.create_attachment(storename=attach_loc,
                                                original_filename=os.path.basename(filepath),
                                                file_created_datetime=file_created_datetime,
                                                guid=attachment_guid,
                                                image_type=mime_type,
                                                url=url,
                                                agent_id=agent_id,
                                                copyright=copyright)
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

    # if the basenames are the same, it removes them.
    def clean_duplicate_basenames(self, filepath_list):
        basename_list = [os.path.basename(filepath) for filepath in filepath_list]
        duplicates = [item for item, count in collections.Counter(basename_list).items() if count > 1]

        # Write out duplicates file
        for duplicate in duplicates:
            res = [item for item in filepath_list if duplicate in item]
            self.duplicates_file.write(f'\nDuplicate: {duplicate}\n')

            for dupe_path in res:
                size = os.path.getsize(dupe_path)
                self.logger.debug(f"dupe_path: {dupe_path}")
                self.duplicates_file.write(f"\t {self.format_filesize(size)}: {dupe_path}\n")
        seen_basenames = set()
        unique_filepaths = []
        for filepath in filepath_list:
            basename = os.path.basename(filepath)
            if basename not in seen_basenames:
                seen_basenames.add(basename)
                unique_filepaths.append(filepath)
        return unique_filepaths

    def convert_image_if_required(self, filepath):
        jpg_found = False
        tif_found = False
        deleteme = None
        filename, filename_ext = self.split_filepath(filepath)
        if filename_ext == "jpg" or filename_ext == "jpeg":
            jpg_found = filepath
        if filename_ext == "tif" or filename_ext == "tiff":
            tif_found = filepath
        if not jpg_found and tif_found:
            self.logger.debug(f"  Must create jpg for {filepath} from {tif_found}")
            try:
                jpg_found, output = self.tiff_to_jpg(tif_found)
                self.logger.info(f"Converted to: {jpg_found}")
            except TimeoutError:
                self.logger.error(f"Timeout converting {tif_found}")
            except subprocess.TimeoutExpired:
                self.logger.error(f"Timeout converting {tif_found}")
            except ConvertException:
                self.logger.error(f"  Conversion failure for {tif_found}; skipping.")
                return False

            if not os.path.exists(jpg_found):
                self.logger.error(f"  Conversion failure for {tif_found}; skipping.")
                self.logger.debug(f"Imagemagik output: \n\n{output}\n\n")
                return False
            deleteme = jpg_found
            if not jpg_found and tif_found:
                self.logger.debug(f"  No valid files for {filepath.full_path}")
                return False
        if os.path.getsize(jpg_found) < 1000:
            self.logger.info(f"This image is too small; {os.path.getsize(jpg_found)}, skipping.")
            return False
        return deleteme

    def upload_filepath_to_image_database(self, filepath, redacted=False):

        deleteme = self.convert_image_if_required(filepath)
        if deleteme is not None:
            upload_me = deleteme
        else:
            upload_me = filepath

        self.logger.debug(
            f"about to import to client:- {redacted}, {upload_me}, {self.collection_name}, {upload_me}")

        url, attach_loc = self.image_client.upload_to_image_server(upload_me,
                                                                   redacted,
                                                                   self.collection_name,
                                                                   filepath)
        if deleteme is not None:
            os.remove(deleteme)
        return (url, attach_loc)

    def remove_imported_filepaths_from_list(self,filepath_list):
        keep_filepaths=[]
        for cur_filepath in filepath_list:
            if not self.image_client.check_image_db_if_filepath_imported(cur_filepath, exact=True):
                keep_filepaths.append(cur_filepath)
        return keep_filepaths

    def remove_imported_filenames_from_list(self,filepath_list):
        keep_filepaths=[]

        for cur_filepath in filepath_list:
            cur_filename = os.path.basename(cur_filepath)
            cur_file_base, cur_file_ext = cur_filename.split(".")

            if not self.image_client.check_image_db_if_filename_imported(self.collection_name,cur_file_base + ".jpg", exact=True):
                keep_filepaths.append(cur_filepath)
        return keep_filepaths



    def import_to_imagedb_and_specify(self, filepath_list, collection_object_id, agent_id, force_redacted=False, copyright_filepath_map=None):
        for cur_filepath in filepath_list:
            # because we'll convert it to a .jpg for purposes of serving and attching to specify
            if_i_were_a_jpg_name = os.path.splitext(os.path.basename(cur_filepath))[0] + '.jpg'

            if force_redacted:
                is_redacted=True
            else:
                is_redacted = self.attachment_utils.get_is_collection_object_redacted(collection_object_id)


            #  Joe bad - does an implicit "check filename if imported"; will fail for iz case.
            (url, attach_loc) = self.upload_filepath_to_image_database(cur_filepath, redacted=is_redacted)

            try:

                copyright = None
                if copyright_filepath_map is not None:
                    if cur_filepath in copyright_filepath_map:
                        copyright = copyright_filepath_map[cur_filepath]
                self.import_to_specify_database(cur_filepath,
                                                attach_loc,
                                                url,
                                                collection_object_id,
                                                agent_id,
                                                copyright=copyright)
            except Exception as e:
                self.logger.debug(
                    f"Upload failure to image server for file: \n\t{cur_filepath}")
                self.logger.debug(f"Exception: {e}")

    def check_for_valid_image(self,full_path):
        # self.logger.debug(f"Ich importer verify file: {full_path}")
        if not filetype.is_image(full_path):
            logging.debug(f"Not identified as a file, looks like: {filetype.guess(full_path)}")
            if full_path.lower().endswith(".tif") or full_path.lower().endswith(".tiff"):
                print("Tiff file misidentified as not an image, overriding auto-recognition")
            else:
                return False

        filename = os.path.basename(full_path)
        if "." not in filename:
            self.logger.debug(f"Rejected; no . : {filename}")

            return False
        return True