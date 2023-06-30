"""this file will be used to parse the data from Picturae into an uploadable format to Specify"""
import os
from datetime import date

import pandas as pd


# may not need
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


def file_present(import_date):
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
        raise ValueError(f"subdirectory for {date.today()} not present")


def csv_read_folder(folder_string, import_date: str):
    """reads in folder_csv data for given date
    args:
        folder_string: denotes whether specimen or folder level data
        import_date: datestring for custom date in form YYYY-M-D, only used when override = True"""


    folder_path = 'picturae_csv/' + str(import_date) + '/picturae_' + str(folder_string) + '(' + \
                   str(import_date) + ').csv'

    folder_csv = pd.read_csv(folder_path)

    return folder_csv

def csv_merge(fold_csv: pd.DataFrame, spec_csv: pd.DataFrame):
    """csv_merge: merges the folder_csv and the specimen_csv on barcode
       args:
            fold_csv: folder level csv to be input as argument for merging
            spec_csv: specimen level csv to be input as argument for merging """

    # checking if columns to merge contain same data
    if (set(fold_csv['specimen_barcode']) == set(spec_csv['specimen_barcode'])) is True:

        # removing duplicate columns
        # (Warning! will want to double-check whether these columns are truly the
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







# def csv_colnames():

### under this point column transformations will be done through a series of functions


### after file is gotten into clean importable form, set import conditions and protocol functions

### final database query functions, to test if data in data base

def master_fun():
    """runs all functions"""
    # file_present()
    file_present(import_date="2023-6-28")


master_fun()

