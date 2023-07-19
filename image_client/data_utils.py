"""Docstring: This is a utility file, outlining various useful functions to be used
   for herbology related tasks
"""
import pandas as pd
import pymysql as psq
import csv
import re
from datetime import datetime
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


def remove_non_numerics(string: str):
    """remove_non_numerics: A small data_cleaning function to remove numerics from a string
    args:
        string: representing a string
    returns:
        re.sub: a string with only numerics, use .apply on dataframe objects"""
    return re.sub('[^0-9]+', '', string)

def replace_apostrophes(string: str):
    """replaces apostrophes like in possessive adjectives in order to not confuse quotation syntax
    args:
        string: a string containing an apostrophe
    returns:
        re.sub: a string with all apostrophes replaces by escape symbol"""

    return re.sub("'", "`", string)


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
