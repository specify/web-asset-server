"""Docstring: This is a utility file, outlining various useful functions to be used
   for botany related data related tasks
"""
from datetime import datetime
import sys
import numpy as np
import pandas as pd
import csv
import re
import os
from PIL import Image
pd.set_option('expand_frame_repr', False)


# String and numeric reformating tools

def str_to_bool(value: str):
    """str_to_bool: will take a column with string 'True' & 'False' and convert to true booleans.
                    Most useful when used with .apply function

        args:
            value: string value to convert to boolean
        returns:
            boolean conversion of string value.
    """
    return value.lower() == 'true'


def remove_non_numerics(string: str):
    """remove_non_numerics: A small data_cleaning function to remove numerics from a string
    args:
        string: representing a string
    returns:
        re.sub: a string with only numerics, use .apply on dataframe objects"""
    return re.sub('[^0-9]+', '', string)


def replace_apostrophes(string: str):
    """replaces apostrophes in possessive adjectives with double quotes to be readable by mysql
    args:
        string: a string containing an apostrophe
    returns:
        re.sub: a string with all apostrophes replaces by double quotes
    """
    # using double quotes on one and single on the other is actually important this time
    return re.sub("'", '"', string)


def move_first_substring(string: str, n_char: int):
    """move_first_substring: will move first n letters from beginning to end of string
       args:
            string: any string
        returns:
            string: a string the first n characters moved to end
        """
    if len(string) <= n_char:
        return string
    else:
        return string[n_char+1:] + string[0:n_char+1]


def assign_titles(first_last, name: str):
    """assign_titles:
            function designed to separate out titles in names into a new title column
        args:
            first_last: whether the name is a first or a last name with string 'first' 'last'
            name: the name string from which to separate out the titles.
    """
    # to lower to standardize matching
    titles = ['mr.', 'mrs.', 'ms.', 'dr.', 'jr.', 'sr.', 'ii', 'iii', 'ii', 'v', 'vi', 'vii', 'viii', 'ix']
    title = ""
    new_name = ""

    # Split the full name into words
    if pd.notna(name):
        name_parts = name.split()
    # Find the title in the name_parts

        if first_last == "first" and (name_parts[0].lower() in titles):
            new_name = " ".join(name_parts[1:])
            title = name_parts[0]

        elif first_last == "last" and (name_parts[-1].lower() in titles):
            new_name = " ".join(name_parts[:-1])
            title = name_parts[-1]
        else:
            # If no title is found, assign the full name to the first name
            new_name = name
    else:
        new_name = name

    return new_name, title


def roman_to_int(string):

    """convert_roman_numeral: takes a string, and replaces roman numerals with integer.
                                Be careful of strings with non-numeral capital Is, Vs etc..
       args:
            string: any string with roman numerals, can be used to loop through elements in a list or vector.
        returns:
            output: a string where all roman numerals are replaced with integers."""

    roman_numerals = {'I': 1, 'V': 5, 'X': 10,
                      'L': 50, 'C': 100, 'D': 500, 'M': 1000}
    output = ''
    i = 0

    while i < len(string):
        if string[i] in roman_numerals:
            numeral_start = i
            while i < len(string) and string[i] in roman_numerals:
                i += 1
            numeral_end = i
            roman_numeral = string[numeral_start:numeral_end]
            integer_value = 0
            for j in range(len(roman_numeral)):
                if j + 1 < len(roman_numeral) and roman_numerals[roman_numeral[j]] < \
                           roman_numerals[roman_numeral[j + 1]]:

                    integer_value -= roman_numerals[roman_numeral[j]]
                else:
                    integer_value += roman_numerals[roman_numeral[j]]
            output += str(integer_value)

        else:
            output += string[i]
            i += 1

    return output


def string_converter(df: pd.DataFrame, column: str, option: str):
    """function to turn string with decimal points into string or int with no decimals
       args:
            df: dataframe to modify
            column: string name of column to modify
            option: end result output
        returns:
            df: a dataframe with the modified column
    """
    if option == "str":
        df[column] = df[column].fillna(0)
        df[column] = pd.to_numeric(df[column], errors='coerce')
        df[column] = df[column].astype(int).astype(str)
        return df
    elif option == "int":
        df[column] = df[column].fillna(0)
        df[column] = pd.to_numeric(df[column], errors='coerce')
        df[column] = df[column].astype(int)
        return df
    else:
        return "Invalid input"


def switch_date_format(df: pd.DataFrame, date_col: str, format_to: str):
    """switch_date_format: changes dates from m/d/y, to d/m/y, or vice versa
        args:
            df: a pandas dataframe with date data.
            date_col: name of column with date info
            format_to: desired end format of string
        returns:
            df: a pandas_df with reformatted date column
    """
    if format_to == '%d/%m/%Y':
        df[date_col] = pd.to_datetime(df[date_col], format='%m/%d/%Y').dt.strftime('%d/%m/%Y')
    elif format_to == '%m/%d/%Y':
        df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y').dt.strftime('%m/%d/%Y')

    else:
        print('not valid format')

    return df


def to_decimal_degrees(coord: str, num_digits: int):
    """to_decimal_degrees: this function is for the conversion of degrees from
       hours, minutes, seconds format to straight decimal degrees.
       args:
            coord: the coordinate string to convert to decimal.
        returns:
            num_coord: the new coordinate converted into numeric decimal format"""

    deg, minutes, seconds, direction = re.split('[°\'"]', coord)

    num_coord = (float(deg) + float(minutes) / 60 + float(seconds) / (60 * 60)) * \
                (-1 if direction in ['W', 'S'] else 1)

    return round(num_coord, num_digits)


def zero_out_barcode(number):
    """changes barcode to specify barcode with leading zeroes, function made for lapply"""
    return str(number).zfill(9)


# taxon parsing tools, tools that modify or parse taxon columns and info,
def separate_qualifiers(tax_frame: pd.DataFrame, tax_col: str):
    """seperate_qualifiers: separates out the parsed taxa and the cf qualifier into new columns
                            qualifier to be stored in new 'qualifier' column.
        args:
            tax_frame: dataframe containing taxon string column, from which qualifiers need to be parsed
            tax_col: the name of the tax column which we want to parse.
        returns:
            tax_frame: a dataframe with new qualifier column parsed from tax column.
        """

    tax_frame['qualifier'] = pd.NA

    qual_regex = ['cf.', 'aff.', 'vel aff.']
    for qual in qual_regex:
        cf_mask = tax_frame[tax_col].str.contains(f"{qual}")
        if len(cf_mask) > 0:
        # setting default to species qualifier
            tax_frame.loc[cf_mask, 'qualifier'] = qual

    # removing trailing whitespace
    tax_frame['qualifier'] = tax_frame['qualifier'].str.strip()

    tax_frame[tax_col] = tax_frame[tax_col].apply(remove_qualifiers)

    return tax_frame


def remove_qualifiers(tax_string: str):
    """remove_qualifiers: removes qualifiers such as cf. or aff. from any taxon string.
        args:
            tax_string: string of taxon name , which one wants to remove qualifiers from.
        returns:
            tax_string: a string without qualifier substrings present.
    """
    qual_list = [" cf.", "cf.", "vel aff.", " vel aff.", " aff.", "aff."]
    for qual_str in qual_list:
        tax_string = tax_string.replace(qual_str, "")

    return tax_string


def extract_after_subtax(text):
    """extract_after_subtax: will take any substring after a subtaxa/intrataxa rank pattern,
        and stores it in a variable. Useful for parsing taxon names
        args:
            text: the verbatim taxon name that will be parsed.
        returns:
            extracted_text: substring after subtaxa rank"""
    patterns = ["subsp\.", "var\.", "subvar\.", "f\.", "subform\."]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            start = match.end()
            extracted_text = text[start:].strip()
            return extracted_text

    return None


# list and dictionary tools: these tools change the ordering or formatting of lists and dictionaries

def write_list_to_csv(file_path: str, data_list: list, col_name: str):
    """write_list_to_csv: writes a list of information to a csv column.

        args:
            file_path: destination for csv file
            data_list: list to write to csv
            col_name: column name in which list data will be stored
    """
    with open(file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([col_name])
        csv_writer.writerows(data_list)


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

# directory tools will modify directories, and parse directory info


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


def create_test_images(barcode_list: list, date_string: str):
    """create_test_images:
            creates a number of standard test images in a range of barcodes,
            and with a specific date string
       args:
            barcode_list: a list or range() of barcodes that
                          you wish to create dummy images for.
            date_string: a date string , with which to name directory
                         in which to create and store the dummy images
    """
    image = Image.new('RGB', (200, 200), color='red')

    barcode_list = barcode_list
    for barcode in barcode_list:
        expected_image_path = f"picturae_img/{date_string}/CAS{barcode}.JPG"
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

# process tools: tools that will time or prompt running processes


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


class Timer:
    """Timer: class that times how long it takes for a block of code to run. Put at top of file
                set to run at exit
        returns:
            duration: endtime - startime, duration of code block run"""
    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()

    def get_duration(self):
        return self.end_time - self.start_time
