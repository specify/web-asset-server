import os as os
import requests
import logging
import json

KEY = 'ad2063c0-b19a-4349-b8c3-c00ef7e2cc0b'

# calling tropicos api
def call_tropicos_api(full_name):
    """call_tropicos_api: checks the tropicos api if there is a legitimate
                          match for a verbatim name"""

    # searching for exact name match
    response = requests.get(f"http://services.tropicos.org/Name/"
                            f"Search?name={full_name}&type=exact&apikey={KEY}&format=json")


    if response.status_code != 200:
        raise ValueError("Connection Error")

    elif response.status_code == 200:
        response_list = response.json()
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

def check_synonyms(tropicos_id):
    syn_response = requests.get(f"https://services.tropicos.org/Name/{tropicos_id}/"
                                f"AcceptedNames?apikey={KEY}&format=json")

    logging.info(f"response_code: {syn_response.status_code}")

    if syn_response.status_code != 200:
        raise ValueError(f'No Matches on Tropicos: {syn_response.status_code}')

    syn_list = syn_response.json()
    name_list = []
    author_list = []
    print(syn_list)
    if len(syn_list[0]) != 1:
        for dict in syn_list:
            if dict['NomenclatureStatusName'] != 'Invalid' \
                    or dict['NomenclatureStatusName'] != 'Illegitimate' \
                    or dict['nom. ut. rej.,']:
                name_list.append(dict['ScientificName'])
                author_list.append(dict['Author'])
    else:
        print('no synonyms adding to taxon')

    return name_list, author_list


# name, author, fam = call_tropicos_api('Clidemia almedae')
#
# print(name)
# print(author)
# print(fam)
#
#
# name_list, author_list = check_synonyms(name)
#
# print(name_list)

# Clidemea Almedea