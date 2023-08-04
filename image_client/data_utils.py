"""Docstring: This is a utility file, outlining various useful functions to be used
   for herbology related tasks
"""
from datetime import datetime
from datetime import timedelta
import random
import sys
import numpy as np
import pandas as pd
import pymysql as psq
import csv
import re
import os
from PIL import Image
pd.set_option('expand_frame_repr', False)


def data_exporter(query_string: str, local_path: str, fromsql: bool):
    """csv_exporter: creates a table in the database using a SQL query, and writes it to a local file.
    args:
        query_string: mysql query that needs to be written,
        use semicolons to split queries, and triple single quotes for a multiline query
        local_path: destination of file
    returns:
        data file into desired directory
    """
    if fromsql is True:
        connection = psq.connect(host='localhost', user='botanist',
                                 password="password", database="casbotany")

        query = query_string

        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        connection.close()

        with open(local_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([i[0] for i in cursor.description])
            writer.writerows(result)
    else:
        pass

    df_init: pd.DataFrame = pd.read_csv(local_path)

    return df_init


def write_list_to_csv(file_path, data_list):
    with open(file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["FullName"])
        csv_writer.writerows(data_list)


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
#
#
# new_name, title = assign_titles(first_last='last', name="morton Jr.")
# print(new_name)
# print(title)


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


# will be expanded to handle both directions
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


def remove_two_index(value_list, column_list):
    missing_index = []
    for index, entry in enumerate(value_list):
        if entry == '<NA>' or entry == '' or pd.isna(entry):
            value_list.remove(entry)
            missing_index.append(index)

    column_list = [column_list[i] for i in range(len(column_list)) if i not in missing_index]

    return value_list, column_list


def write_dict_to_csv(tax_dict, filename):
    with open(filename, mode='w', newline='') as file:
        fieldnames = ['Barcode', 'FullName', 'AcceptedName']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        writer.writeheader()
        for barcode, info in tax_dict.items():
            row = {'Barcode': barcode, 'FullName': info['FullName'], 'AcceptedName': info['AcceptedName']}
            writer.writerow(row)


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


def create_timestamps(start_time):
    """create_timestamps:
            uses starting and ending timestamps to create window for sql database purge,
            adds 10 second buffer on either end to allow sql queries to populate.
            appends each timestamp record to a csv log.
        args:
            start_time: starting time stamp
            end_time: ending time stamp
    """

    end_time = datetime.now()

    delt_time = timedelta(seconds=15)

    time_stamp_list = [start_time - delt_time, end_time + delt_time]

    csv_file_path = 'csv_purge_sql/upload_time_stamps.csv'

    with open(csv_file_path, 'a', newline='') as csvfile:
        fieldnames = ['StartTime', 'EndTime', 'UploadCode']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if csvfile.tell() == 0:
            writer.writeheader()

            writer.writerow({'StartTime': time_stamp_list[0], 'EndTime': time_stamp_list[1],
                             'UploadCode': random.randint(100000, 999999)})

    print(f"The timestamps have been added to '{csv_file_path}'.")


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


class Timer:
    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime.now()

    def get_duration(self):
        return self.end_tim - self.start_time


