"""Docstring: This is a utility file, outlining various useful functions to be used
   for csv and image import related tasks.
"""

from datetime import datetime
import sys
import numpy as np
import pandas as pd
import os
from PIL import Image
import re


# import list tools
def rewrite_config_date(date:str, filepath:str):
    """used to rewrite date_str in config files for picturae_importer
    args:
        date: the date string in YYYY-MM-DD format to sub into config file.
        filepath: path to config file which you want to change"""
    filename = filepath

    latest_date = r'\1"' + date + r'"\n'

    with open(filename, 'r') as file:
        # Read the contents of the file
        content = file.read()

    # Replace the string
    new_content = re.sub(r'(date_str = )(.*?)\n', latest_date, content)

    with open(filename, 'w') as file:
        # Write the modified content back to the file
        file.write(new_content)


def unique_ordered_list(input_list):
    """unique_ordered_list:
            takes a list and selects only unique elements,
            while preserving order
        args:
            input_list: list which will be made to have
                        only unique elements.
    """
    unique_elements = []
    for element in input_list:
        if element not in unique_elements:
            unique_elements.append(element)
    return unique_elements


def remove_two_index(value_list, column_list):
    new_value_list = []
    new_column_list = []
    for entry, column in zip(value_list, column_list):
        if isinstance(entry, float) and np.isnan(entry):
            continue

        elif pd.isna(entry):
            continue

        elif entry == '<NA>' or entry == '':
            continue

        new_value_list.append(entry)
        new_column_list.append(column)

    return new_value_list, new_column_list


# import process/directory tools
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


def create_test_images(barcode_list: list, date_string: str, color: str):
    """create_test_images:
            creates a number of standard test images in a range of barcodes,
            and with a specific date string
       args:
            barcode_list: a list or range() of barcodes that
                          you wish to create dummy images for.
            date_string: a date string , with which to name directory
                         in which to create and store the dummy images
    """
    image = Image.new('RGB', (200, 200), color=color)

    barcode_list = barcode_list
    for barcode in barcode_list:
        expected_image_path = f"picturae_img/PIC_{date_string}/CAS{barcode}.JPG"
        os.makedirs(os.path.dirname(expected_image_path), exist_ok=True)
        print(f"Created directory: {os.path.dirname(expected_image_path)}")
        image.save(expected_image_path)

def get_max_subdirectory_date(parent_directory: str):
    """get_max_subdirectory_date: lists every subdirectory in a directory, presuming data is organized by date, in any
                                dash divided fomrat Y-M-D, D-M-Y etc..., pulls the largest date from the list.
                                Useful for updating config files and functions with dependent date variables
        args:
            parent_directory: the directory from which we want to list subdirectories with max date."""
    subdirect = [d for d in os.listdir(parent_directory) if os.path.isdir(os.path.join(parent_directory, d))]
    latest_date = None
    for date in subdirect:
        try:
            date = datetime.strptime(date, "%Y-%m-%d")
            if latest_date is None or date > latest_date:
                latest_date = date
        except ValueError:
            continue
    return latest_date


def cont_prompter():
    """cont_prompter:
            placed critical step after database checks, prompts users to
            confirm in order to continue. Allows user to check logger texts to make sure
            no unwanted data is being uploaded.
    """
    while True:
        user_input = input("Do you want to continue? (y/n): ")
        if user_input.lower() == "y":
            break
        elif user_input.lower() == "n":
            sys.exit("Script terminated by user.")
        else:
            print("Invalid input. Please enter 'y' or 'n'.")