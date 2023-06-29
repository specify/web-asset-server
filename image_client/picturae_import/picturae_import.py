"""this file will be used to parse the data from Picturae into an uploadable format to Specify"""
import os
from datetime import date


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
       checks if filepath with correct name in working directory,
       checks if file is on current date
       args:

    """
    to_current_directory()
    files_present = 0
    if date_override is None:

        dir_sub = os.path.isdir(str("Production/") + str(date.today()))

        if dir_sub is True:
            folder_path = 'picturae_csv/' + str(date.today()) + '/picturae_folder(' + \
                            str(date.today()) + ').csv'

            specimen_path = 'picturae_csv/' + str(date.today()) + '/picturae_specimen(' + \
                            str(date.today()) + ').csv'

            if os.path.exists(folder_path):
                files_present += 1
            else:
                raise ValueError("Folder csv does not exist")

            if os.path.exists(specimen_path):
                print("Specimen csv exists!")
                files_present += 1
            else:
                raise ValueError("Specimen_csv does not exist")
        else:
            raise ValueError(f"subdirectory for {date.today()} not present")
    else:
        folder_path = 'picturae_csv/' + new_date + '/picturae_folder(' + \
                      new_date + ').csv'

        specimen_path = 'picturae_csv/' + new_date + '/picturae_specimen(' + \
                        new_date + ').csv'

        if os.path.exists(folder_path):
            print("Folder csv exists!")
            files_present += 1
        else:
            raise ValueError("Folder csv does not exist")

        if os.path.exists(specimen_path):
            files_present += 1
            print("Specimen csv exists!")
        else:
            raise ValueError("Specimen csv does not exist")

    return files_present


# change filename path manually for now

# def file_empty():
"""will test if csv files contain rows or not"""


def master_fun():
    """runs all functions"""
    file_present(file_present(date_override=True, new_date="2023-6-28"))
