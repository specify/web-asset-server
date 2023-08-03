import urllib.parse

import requests
import logging
import json
from urllib.parse import urlencode, quote_plus
from image_client.data_utils import unique_ordered_list

KEY = 'ad2063c0-b19a-4349-b8c3-c00ef7e2cc0b'

# calling tropicos api
def call_tropicos_api(full_name):
    """call_tropicos_api: checks the tropicos api if there is a legitimate
                          match for a verbatim name"""

    # param_string = urlencode(param_dict, quote_via=quote_plus)

    query_params = {'name': full_name, 'type': 'exact',
                    'apikey': KEY, 'format': 'json'}

    encoded = urllib.parse.urlencode(query_params)
    tax_url = f"http://services.tropicos.org/Name/Search?{encoded}"
    print(tax_url)
    taxon_url = f"http://services.tropicos.org/Name/Search?" \
                f"name={full_name}&type=exact&apikey={KEY}&format=json"

    print(taxon_url)

    # searching for exact name match
    response = requests.get(taxon_url)


    if response.status_code != 200:
        raise ValueError(f"Connection Error: {response.status_code}")

    elif response.status_code == 200:
        response_list = response.json()
        print(response_list)
        tax_dict = response_list[0]
        if len(tax_dict) != 1:

            if tax_dict['NomenclatureStatusName'] != 'Invalid' \
                    or tax_dict['NomenclatureStatusName'] != 'Illegitimate'\
                    or tax_dict['nom. ut. rej.,']:

                name_id = tax_dict['NameId']

                author_sci = tax_dict['ScientificNameWithAuthors']

                family = tax_dict['Family']

            else:
                raise ValueError('illegitimate name')

            return name_id, author_sci, family
        else:
            match_status = "No Match"
            return match_status, match_status, match_status

def check_synonyms(tropicos_id, mode: str):
    """check_synonyms:
            retrieves synonym list from tropicos, and pulls accepted name,
        args:
            tropicos_id: number id for tropicos taxon
            acc_syn: only takes argument "Synonyms" or "AcceptedNames", for api query

    """
    syn_response = requests.get(f"https://services.tropicos.org/name/{tropicos_id}/"
                                f"{mode}?apikey={KEY}&format=json")

    logging.info(f"response_code: {syn_response.status_code}")

    if syn_response.status_code != 200:
        raise ValueError(f'No Matches on Tropicos: {syn_response.status_code}')

    syn_list = syn_response.json()

    name_list = []
    print(syn_list)
    if len(syn_list[0]) != 1:
        first_iteration = True
        for dict in syn_list:
            accept_name = dict.get('AcceptedName', {}).get('ScientificName')
            synonym = dict.get('SynonymName', {}).get('ScientificName')
            if first_iteration:
                name_list.append(accept_name)
                first_iteration = False
            name_list.append(synonym)
    else:
        print('no synonyms')
    name_list = unique_ordered_list(name_list)

    return name_list





name, author, fam = call_tropicos_api('Arctostaphylos glandulosa')

print(name)
print(author)
print(fam)


synonym_list = check_synonyms(tropicos_id=name, mode='Synonyms')

accept_list = check_synonyms(tropicos_id=name, mode='AcceptedNames')

#

print(synonym_list)
print(accept_list)


# Clidemia almedae


# import requests

# def tnrs_resolve(query):
#     """
#     Use TNRS to resolve a scientific name query.
#
#     Args:
#         query (str): The scientific name query.
#
#     Returns:
#         dict: A dictionary containing the TNRS response in JSON format.
#     """
#     base_url = 'https://tnrs.biendata.org/api/tnrs/match_names'
#     payload = {
#         'names': [query],
#         'fuzzy': 'false',
#         'multiple_match_behavior': 'none',
#         'context': 'TROPICOS',
#     }
#
#     try:
#         response = requests.post(base_url, json=payload)
#         response.raise_for_status()
#         return response.json()
#     except requests.exceptions.RequestException as e:
#         print(f"Error: {e}")
#         return None
#
# # Example usage
# if __name__ == "__main__":
#     scientific_name = "Quercus alba"
#     tnrs_response = tnrs_resolve(scientific_name)
#
#     if tnrs_response:
#         # TNRS returns matches, ambiguous matches, and unmatched names
#         matches = tnrs_response.get('names')
#         if matches:
#             for match in matches:
#                 print(f"Matched name: {match['submittedName']} -> {match['matchedName']}")
#         else:
#             print("No matches found.")
#     else:
#         print("Unable to resolve the name.")