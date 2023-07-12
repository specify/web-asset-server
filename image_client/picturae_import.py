"""this file will be used to parse the data from Picturae into an uploadable format to Specify"""
import sys

import picturae_config
import os
from datetime import date
from data_utils import *
import pandas as pd
from importer import Importer
from db_utils import DbUtils
from specify_db import SpecifyDb
from botany_importer import BotanyImporter
import logging


class DataOnboard(Importer):
    def __init__(self, date_string):
        super().__init__(picturae_config, "Botany")
        self.date_use = date_string
        self.logger = logging.getLogger('DataOnboard')
        self.barcode_list = []
        self.image_list = []
        self.record_full = pd.DataFrame

    def to_current_directory(self):
        """to_current_directory: changes current directory to .py file location
            args:
                none
            returns:
                resets current directory to source file location
        """
        current_file_path = os.path.abspath(__file__)

        directory = os.path.dirname(current_file_path)

        os.chdir(directory)


    def file_present(self):
        """file_present:
           checks if correct filepath in working directory,
           checks if file is on current date, or input date
           checks if file folder is present
           args:
                override: takes boolean to specify whether to override today's date for custom date
                new_date: datestring for custom date in form YYYY-M-D, only used when override = True"""

        self.to_current_directory()

        dir_sub = os.path.isdir(str("picturae_csv/") + str(self.date_use))

        if dir_sub is True:
            folder_path = 'picturae_csv/' + str(self.date_use) + '/picturae_folder(' + \
                           str(self.date_use) + ').csv'

            specimen_path = 'picturae_csv/' + str(self.date_use) + '/picturae_specimen(' + \
                             str(self.date_use) + ').csv'

            if os.path.exists(folder_path):
                print("Folder csv exists!")
            else:
                raise ValueError("Folder csv does not exist")

            if os.path.exists(specimen_path):
                print("Specimen csv exists!")
            else:
                raise ValueError("Specimen csv does not exist")
        else:
            raise ValueError(f"subdirectory for {self.date_use} not present")

    def csv_read_folder(self, folder_string):
        """reads in folder_csv data for given date
        args:
            folder_string: denotes whether specimen or folder level data
            import_date: datestring for custom date in form YYYY-M-D, only used when override = True"""

        folder_path = 'picturae_csv/' + str(self.date_use) + '/picturae_' + str(folder_string) + '(' + \
                       str(self.date_use) + ').csv'

        folder_csv = pd.read_csv(folder_path)

        return folder_csv

    def csv_merge(self):
        """csv_merge: merges the folder_csv and the specimen_csv on barcode
       args:
            fold_csv: folder level csv to be input as argument for merging
            spec_csv: specimen level csv to be input as argument for merging """
        fold_csv = self.csv_read_folder("folder")
        spec_csv = self.csv_read_folder("specimen")

    # checking if columns to merge contain same data
        if (set(fold_csv['specimen_barcode']) == set(spec_csv['specimen_barcode'])) is True:
        # removing duplicate columns
        # (Warning! will want to double-check whether these columns are truly the
        # same between datasets when more info received)

            common_columns = list(set(fold_csv.columns).intersection(set(spec_csv.columns)))

            common_columns.remove('specimen_barcode')

            spec_csv = spec_csv.drop(common_columns, axis=1)

            # completing merge on barcode
            self.record_full = pd.merge(fold_csv, spec_csv,
                                        on='specimen_barcode', how='inner')

        else:
            raise ValueError("Barcode Columns do not match!")





    def csv_colnames(self):
        """csv_colnames: function to be used to rename columns to specify standards"""
        # remove columns !! review when real dataset received

        col_names = self.record_full.columns

        print(col_names)
        cols_drop = ['application_batch', 'csv_batch', 'object_type', 'filed_as_family',
                     'barcode_info', 'Notes', 'Feedback']
        # dropping empty columns
        self.record_full = self.record_full.drop(columns=cols_drop)

        self.record_full = self.record_full.dropna(axis=1, how='all')

        # some of these are just placeholders for now

        col_dict = {'specimen_barcode': 'CatalogNumber',
                    'path_jpg': 'image_path',
                    'collector_number': 'collector_number',
                    'collector_first_name 1': 'collector_first_name1',
                    'collector_middle_name 1': 'collector_middle_name1',
                    'collector_last_name 1': 'collector_last_name1',
                    'collector_first_name 2': 'collector_first_name2',
                    'collector_middle_name 2': 'collector_middle_name2',
                    'collector_last_name 2': 'collector_last_name2',
                    'Genus': 'Genus',
                    'Species': 'Species',
                    'Qualifier': 'Qualifier',
                    'Hybrid': 'Hybrid',
                    'Taxon ID': 'RankID',
                    'Author': 'Author'}

        self.record_full = self.record_full.rename(columns=col_dict)


    # def mapping_AuthorID(df: pd.DataFrame):

    # def mapping_LocalityID(df: pd.Dataframe):

    # def mapping_TaxonID(df: pd.Dataframe):


    # under this point column transformations will be done through a series of functions
    # will reuse/modify some wrangling functions from data standardization


    # def col_clean():
    #    """will reformat and clean dataframe until ready for upload.
    #       **Still need format end-goal
    #       """


    # after file is wrangled into clean importable form,
    # and QC protocols to follow before import
    # QC measures needed here ? before proceeding.

    def barcode_has_record(self):
        self.record_full['CatalogNumber'] = self.record_full['CatalogNumber'].apply(remove_non_numerics)
        self.record_full['CatalogNumber'] = self.record_full['CatalogNumber'].astype(str)
        self.record_full['barcode_present'] = None
        for index, row in self.record_full.iterrows():
            barcode = os.path.basename(row['CatalogNumber'])
            barcode = barcode.zfill(9)
            sql = f"select CatalogNumber from casbotany.collectionobject " \
                  f"where CatalogNumber = {barcode}"
            db_barcode = self.specify_db_connection.get_one_record(sql)
            if db_barcode is None:
                row['barcode_present'] = False
            else:
                row['barcode_present'] = True


    def image_has_record(self):

        self.record_full['image_present'] = None
        for index, row in self.record_full.iterrows():
            file_name = os.path.basename(row['image_path'])
            file_name = file_name.lower()
            sql = f"select origFilename from casbotany.attachment " \
                  f"where origFilename = {file_name}"
            db_name = self.specify_db_connection.get_one_record(sql)
            if db_name is None:
                row['image_present'] = True
            else:
                row['image_present'] = False


# def check_attachment(df: pd.DataFrame):

# under construction
    # although this could be done on a row be row basis,
    # it is faster to make booleans now, and filter later in the process function

    def check_barcode_match(self):
        """checks if filepath barcode matches catalog number barcode"""
        self.record_full['file_path_digits'] = self.record_full['image_path'].apply(
            lambda path: self.get_first_digits_from_filepath(path, field_size=9)
        )
        print(self.record_full['file_path_digits'])
        self.record_full['is_barcode_match'] = self.record_full.apply(lambda row: row['file_path_digits'] ==
                                                                      row['CatalogNumber'].zfill(9), axis=1)

        self.record_full = self.record_full.drop(columns='file_path_digits')


    def check_if_images_present(self):
        """checks that each image exists, creating boolean column for later use"""
        self.record_full['image_valid'] = self.record_full['image_path'].apply(self.check_for_valid_image)

    # think of finding way to make this function logic not so repetitive
    def create_file_list(self):
        """creates a list of imagepaths and barcodes for upload,
        after checking conditions established in earlier functions"""

        for index, row in self.record_full.iterrows():
            if row['image_valid'] is False:
                raise ValueError(f"image {row['image_path']} is not valid ")

            if row['is_barcode_match'] is False:
                raise ValueError(f"image barcode {row['image_path']} does not match "
                                 f"{row['CatalogNumber']}")

            if row['barcode_present'] is True & row['image_present'] is True:
                raise ValueError(f"record {row['CatalogNumber']} and image {row['image_path']} "
                                 f"already in database")

            if row['barcode_present'] is True & row['image_present'] is False:
                self.logger.debug(f"record {row['CatalogNumber']} "
                                  f"already in database, appending image")
                self.image_list.append(row['image_path'])

            if row['barcode_present'] is False & row['image_present'] is True:
                self.logger.debug(f"image {row['image_path']} "
                                  f"already in database, appending record")
                self.barcode_list.append(row['CatalogNumber'])

            else:
                self.image_list.append(row['image_path'])
                self.barcode_list.append(row['CatalogNumber'])
            # a stopping point, to allow user to read logger messages,
            # and decide whether to proceed
            while True:
                user_input = input("Do you want to continue? (y/n): ")
                if user_input.lower() == "y":
                    break
                elif user_input.lower() == "n":
                    sys.exit("Script terminated by user.")
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")

    def create_csv_skeleton(self):
        """used to assign columns to database tables using sql"""
        self.record_full = self.record_full[self.record_full['CatalogNumber'].isin(self.barcode_list)]
        for index, row in self.record_full.iterrows():
            row


    # def run_all_methods(self):
    #     # setting directory
    #     self.to_current_directory()
    #     # verifying file presence
    #     self.file_present()
    #     # merging csv files
    #     full_frame = self.csv_merge()
    #     # renaming columns
    #     full_frame = self.csv_colnames()
    #     # checking if barcode record present in database
    #     full_frame = self.barcode_has_record()
    #     # checking if attachment record present in database
    #     # checking if barcode has valid image file
    #     full_frame = self.check_if_images_present()
    #     full_frame = self.check_barcode_match()
    #     # creating skeleton
    #     # finished

