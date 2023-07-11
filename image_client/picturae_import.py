"""this file will be used to parse the data from Picturae into an uploadable format to Specify"""
import os
from datetime import date
from data_utils import *
import pandas as pd
from importer import Importer


def to_current_directory():
    """to_current_directory: changes current directory to .py file location
       args:
            none
       returns:
            resets current directory to source file location
    """
    current_file_path = os.path.abspath(__file__)

    directory = os.path.dirname(current_file_path)

    os.chdir(directory)


def file_present(import_date: str):
    """file_present:
       checks if correct filepath in working directory,
       checks if file is on current date, or input date
       checks if file folder is present
       args:
            override: takes boolean to specify whether to override today's date for custom date
            new_date: datestring for custom date in form YYYY-M-D, only used when override = True"""

    to_current_directory()

    dir_sub = os.path.isdir(str("picturae_csv/") + str(import_date))

    if dir_sub is True:
        folder_path = 'picturae_csv/' + str(import_date) + '/picturae_folder(' + \
                       str(import_date) + ').csv'

        specimen_path = 'picturae_csv/' + str(import_date) + '/picturae_specimen(' + \
                         str(import_date) + ').csv'

        if os.path.exists(folder_path):
            print("Folder csv exists!")
        else:
            raise ValueError("Folder csv does not exist")

        if os.path.exists(specimen_path):
            print("Specimen csv exists!")
        else:
            raise ValueError("Specimen csv does not exist")
    else:
        raise ValueError(f"subdirectory for {import_date} not present")


def csv_read_folder(folder_string, import_date: str):
    """reads in folder_csv data for given date
    args:
        folder_string: denotes whether specimen or folder level data
        import_date: datestring for custom date in form YYYY-M-D, only used when override = True"""

    folder_path = 'picturae_csv/' + str(import_date) + '/picturae_' + str(folder_string) + '(' + \
                  str(import_date) + ').csv'

    folder_csv = pd.read_csv(folder_path)

    return folder_csv


# def images_present():
    # """images_present, function to verify if corrent number of images,
    # corresponding to image paths in picturae csv files"""


def csv_merge(fold_csv: pd.DataFrame, spec_csv: pd.DataFrame):
    """csv_merge: merges the folder_csv and the specimen_csv on barcode
   args:
        fold_csv: folder level csv to be input as argument for merging
        spec_csv: specimen level csv to be input as argument for merging """

# checking if columns to merge contain same data
    if (set(fold_csv['specimen_barcode']) == set(spec_csv['specimen_barcode'])) is True:

    # removing duplicate columns
    # (Warning! will want to double-check whether these columns are truly the)
    # same between datasets when more info received

        common_columns = list(set(fold_csv.columns).intersection(set(spec_csv.columns)))

        common_columns.remove('specimen_barcode')

        spec_csv = spec_csv.drop(common_columns, axis=1)

        # completing merge on barcode
        record_full = pd.merge(fold_csv, spec_csv,
                               on='specimen_barcode', how='inner')

    else:
        raise ValueError("Barcode Columns do not match!")

    return record_full



def csv_colnames(df: pd.DataFrame):
    """csv_colnames: function to be used to rename columns to specify standards"""
    # remove columns !! review when real dataset received

    col_names = df.columns

    print(col_names)
    cols_drop = ['application_batch', 'csv_batch', 'object_type', 'filed_as_family',
                 'barcode_info', 'Notes', 'Feedback']
    # dropping empty columns
    df = df.drop(columns=cols_drop)

    df = df.dropna(axis=1, how='all')

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

    df = df.rename(columns=col_dict)

    return df


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


# final database query functions, to test if data in database
# want to know , is image and attachment already in database?
# is collection object already in database?
# how do we manage a conflict between records?


# replace database reference to more current table
def barcode_has_record(df: pd.DataFrame):
    """checks whether barcode is present in database already
        args:
            dataframe object with indatabase True, False boolean"""
    df['CatalogNumber'] = df['CatalogNumber'].apply(remove_non_numerics)
    df['CatalogNumber'] = df['CatalogNumber'].astype(str)
    import_barcode_list = list(df['CatalogNumber'])
    print(import_barcode_list)
    query_string = "SELECT CatalogNumber FROM casbotany.collectionobject " \
                   "WHERE CatalogNumber IN ({});".format(', '.join(str(item) for item in import_barcode_list))
    database_samples = data_exporter(query_string=query_string, fromsql=True,
                                     local_path="test_barcodes/barcode_db.csv")
    database_samples['CatalogNumber'] = database_samples['CatalogNumber'].astype(str)
    database_samples = database_samples['CatalogNumber'].tolist()
    print(database_samples)
    df['indatabase'] = None
    for index, barcode in enumerate(import_barcode_list):
        if barcode in database_samples:
            df.at[index, 'indatabase'] = True
        else:
            df.at[index, 'indatabase'] = False


def check_if_images_present(df: pd.DataFrame):
    df['image_valid'] = df['image_path'].apply(Importer.check_for_valid_image())




# def create_csv_skeleton():

# def upload_skeleton_record(df: pd.DataFrame):
    ###


def master_fun():
    """runs all functions"""
    # file_present()
    file_present(import_date='2023-6-28')
    folder_csv = csv_read_folder(folder_string='folder', import_date='2023-6-28')
    specimen_csv = csv_read_folder(folder_string='specimen', import_date='2023-6-28')
    full_csv = csv_merge(folder_csv, specimen_csv)
    full_csv = csv_colnames(full_csv)
    csv_record = barcode_has_record(full_csv)
    image_present = check_if_images_present(full_csv)
    return full_csv


# calling master

master_fun()
