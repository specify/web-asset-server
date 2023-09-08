"""Docstring: This is a utility file, outlining various useful functions to be used
   for parsing taxonomic nomenclature
"""
import pandas as pd
import re
pd.set_option('expand_frame_repr', False)

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
