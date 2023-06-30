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


def file_present(date_override=None, new_date=None):
    """file_present:
       checks if correct filepath in working directory,
       checks if file is on current date, or input date
       checks if file folder is present
       args:
            override: takes boolean to specify whether to override today's date for custom date
            new_date: datestring for custom date in form YYYY-M-D, only used when override = True"""

    to_current_directory()
    folder_date = None

    if date_override is None:
        folder_date = date.today()

    if date_override is True:
        folder_date = new_date

    dir_sub = os.path.isdir(str("picturae_csv/") + str(folder_date))

    if dir_sub is True:
        folder_path = 'picturae_csv/' + str(folder_date) + '/picturae_folder(' + \
                      str(folder_date) + ').csv'

        specimen_path = 'picturae_csv/' + str(folder_date) + '/picturae_specimen(' + \
                        str(folder_date) + ').csv'

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

# change filename path manually for now


# def file_empty(date_override=None, new_date=None):
#     will test if csv files contains any rows or not"""
#
#     if date_override is None:
#         folder_date = date.today()
#
#     elif date_override is True:
#         folder_date = new_date
#
#     path = (str("picturae_csv/") + str(folder_date))
#
#     folder_path = pd.read(path + '/picturae_folder(' + str(folder_date) + ').csv')
#
#     specimen_path = pd.read(path + '/specimen_folder(' + str(folder_date) + ').csv')
#
#     # creating empty boolean for folder csv
#     folder_csv = pd.read_csv(folder_path)
#
#     folder_empty = folder_csv.empty
#
#     # creating empty boolean for specimen csv
#
#     specimen_csv = pd.read_csv(specimen_path)
#
#     specimen_empty = specimen_csv.empty
#     # Raises for empty dataframe
#     if folder_empty is True:
#         raise ValueError("Folder csv contains no data!")
#
#     if specimen_empty is True:
#         raise ValueError("Specimen csv contains no data!")
#
#     print("csv files are populated")


def csv_read_folder(folder_string: str,override=None, new_date=None):
    """reads in folder_csv data for given date
    args:
        folder_string: denotes whether specimen or folder level data
        override: takes boolean to specify whether to override today's date for custom date
        new_date: datestring for custom date in form YYYY-M-D, only used when override = True"""
    folder_date = None
    if override is None:
        folder_date = date.today()
    if override is True:
        folder_date = new_date

    folder_path = 'picturae_csv/' + str(folder_date) + '/picturae_' + str(folder_string) + '(' + \
                   str(folder_date) + ').csv'

    folder_csv = pd.read_csv(folder_path)

    return folder_csv


### will merge both csv files into a master csv file
# def csv_merge():

def master_fun():
    """runs all functions"""
    # file_present()
    file_present(date_override=True, new_date="2023-6-28")


master_fun()

