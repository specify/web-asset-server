#!/usr/bin/env python3
import argparse
import logging
import os
import filetype
import datetime
import requests
from uuid import uuid4
from os.path import splitext
import json
import botany_importer

import settings
from client_utilities import update_time_delta
import sys
from client_utilities import build_url
from client_utilities import generate_token
from client_utilities import get_timestamp
import re

args=None
datetime_now = datetime.datetime.now(datetime.timezone.utc)
TIME_FORMAT="%Y-%m-%d %H:%M:%S%z"
class UploadFailureException(Exception):
    pass

def parse_command_line():

    parser = argparse.ArgumentParser(
        description=f"""
             Tool to import images into the CAS image server. 
             
             Available collections:
             {[x for x in settings.COLLECTION_DIRS.keys()]}
             
             On successful import, output will be:
             original filename,internal filename,URL
             one line per successful import. All timestamps for a single import command will match.
             
             Examples: Import "IMG_123.JPG" from directory structure /Users/joe/Desktop:
               Botany import -t -x '(IMG|img)_[0-9]*.(JPG|jpg|jpeg)' -r /Users/joe/Desktop
               Botany import -t -x '(CAS|cas)[0-9]{7}.(JPG|jpg|jpeg)' -r /images/botany
             """,
        formatter_class=argparse.RawTextHelpFormatter, add_help=True)

    parser.add_argument('-v', '--verbosity',
                               help='verbosity level. repeat flag for more detail',
                               default=0,
                               dest='verbose',
                               action='count')

    parser.add_argument('collection', help='Collection')

    subparsers = parser.add_subparsers(help='Select search or import mode', dest="subcommand")
    # # help='search partial or complete filenames. -w for wildcard searches (mysql "like" format, % for *).')
    search_parser = subparsers.add_parser('search')
    # , help='import filenames or directories, -r for recursive import.'
    import_parser = subparsers.add_parser('import')

    search_parser.add_argument('term')
    search_parser.add_argument('-w',
                        '--wildcard',
                        help='wildcard search',
                        dest='exactdata',
                        action='store_true')

    import_parser.add_argument('-r',
                        '--recursive',
                        help='recursive descent',
                        dest='recursive',
                        action='store_true')

    import_parser.add_argument('-p',
                        '--private',
                        help='private (redacted)',
                        dest='private',
                        action='store_true')

    import_parser.add_argument('-t',
                        '--disable-test',
                        help='Disable default test import mode',
                        dest='disable_test',
                        default=True,
                        action='store_false')
    import_parser.add_argument('-x',
                               '--regular-expressions',
                               help='file(s) are regular expressions (escape for shell!)',
                               dest='regex',
                               default=None,
                               action='store')

    import_parser.add_argument('files', nargs='+')

    return parser.parse_args()

def upload_to_server(full_path,redacted):
    global attach_loc
    local_filename = full_path
    uuid = str(uuid4())
    name, extension = splitext(local_filename)
    attach_loc = uuid + extension
    data = {
        'store': attach_loc,
        'type': 'image',
        'coll': args.collection,
        'token': generate_token(get_timestamp(), attach_loc),
        'original_filename': os.path.basename(local_filename),
        'original_path': full_path,
        'redacted': str(redacted),
        'notes': None,
        'datetime': datetime_now.strftime(TIME_FORMAT)
    }

    files = {
        'image': (attach_loc, open(local_filename, 'rb')),
    }
    r = requests.post(build_url("fileupload"), files=files, data=data)
    if r.status_code != 200:
        print(f"Image upload aborted: {r.status_code}:{r.text}")
        raise UploadFailureException
    else:
        params = {
            'filename': attach_loc,
            'coll': args.collection,
            'type': 'image',
            'token': generate_token(get_timestamp(), attach_loc)
        }

        r = requests.get(build_url("getfileref"), params=params)
        url = r.text
        assert r.status_code == 200

        print(f"{local_filename},{attach_loc},{url}")
    logging.debug("Upload to file server complete")
    return url

def check_image_db_if_already_imported(filename):
    params = {
        'filename': filename,
        'coll': args.collection,
        'exact': False,
        'token': generate_token(get_timestamp(), filename)
    }

    r = requests.get(build_url("getImageRecordByOrigFilename"), params=params)
    if r.status_code == 404:
        logging.debug(f"Checked {filename} against {args.collection} and found no duplicates")
        return False
    if r.status_code == 200:
        logging.debug(f"Checked {filename} - already imported")

        return True
    assert False


def process_file(filepath, filename):
    logging.debug(f"Processing {filepath}{os.path.sep}{filename}", flush=True)
    if filepath is None:
        full_path = filename
    else:
        dirnames = filepath.split(os.path.sep)
        for dirname in dirnames:
            if dirname.startswith('.') and len(dirname) > 1:
                return
        if filepath.endswith(os.path.sep):
            full_path = f"{filepath}{filename}"
        else:
            full_path = f"{filepath}{os.path.sep}{filename}"

    if not os.path.isfile(full_path):
        logging.debug(f"Not a file: {full_path}")
    else:
        if args.regex:
            check_regex = os.path.basename(full_path)
            matched = re.match(args.regex, check_regex)
            is_match = bool(matched)
            logging.debug(f"Check regex {args.regex} on:{check_regex} in dir {filepath}: {is_match}")
            if not is_match:
                return

        if filetype.is_image(full_path):
            if check_image_db_if_already_imported(os.path.basename(full_path)):
                print(f"Image {filename} already imported, skipping..", file=sys.stderr, flush=True)
                return
            if args.disable_test != True:
                is_redacted = False
                if args.collection == "Botany":
                    collection_object_id = botany_importer.get_collection_object_id(full_path)
                    if collection_object_id is None:
                        print(f"Not importing {full_path}; not in system")
                        return
                    is_redacted = botany_importer.get_is_redacted(collection_object_id)

                if args.private:
                    is_redacted = True
                try:
                    url = upload_to_server(full_path,is_redacted)
                    if args.collection == "Botany":
                        botany_importer.import_to_database(full_path,attach_loc,url)
                except UploadFailureException:
                    print(f"Upload failure to image server for file: {full_path}")
        else:
            logging(f"File found, but not image, skipping: {full_path}")



def process_files_or_directories_recursive(path_names):
    for path in path_names:
        for root, d_names, f_names in os.walk(path):
            for cur_file in f_names:
                process_file(root,cur_file)


def process_directory(dirpath):
    for file in os.listdir(dirpath):
        full_path = os.path.join(dirpath, file)
        if not os.path.isdir(full_path):

            process_file(dirpath, file)



def process_file_or_directory(file_list):
    for curfile in file_list:
        if os.path.isdir(curfile):
            process_directory(curfile)
        else:
            process_file(None,curfile)


def search(arg):
    params = {
        'filename': arg,
        'exact': args.exactdata,
        'token': generate_token(get_timestamp(), arg)
    }

    r = requests.get(build_url("getImageByOrigFilename"), params=params)
    print(f"Search result: {r.status_code}")
    if (r.status_code == 404):
        print(f"No records found for {arg}")
        return False
    if r.status_code != 200:
        print(f"Unexpected search result: {r.status_code}; aborting.")
        return
    data = json.loads(r.text)
    print(f"collection, datetime, id, internal_filename, notes, original filename, original path, redacted, universal URL, URL")
    if len(data) == 0:
        print("No match.")
    else:
        for item in data:
            print(f"{item['collection']},{item['datetime']},{item['internal_filename']},{item['notes']},{item['original_filename']},{item['original_path']},{item['redacted']},{item['universal_url']},{item['url']}")


def main(args):
    update_time_delta()
    if args.subcommand == 'search':
        search(args.term)
    else:
        logging.debug("Import mode")
        if args.regex and len(args.files) > 1:
            print("Can't wildcard match on multiple files")
            sys.exit(1)
        if args.recursive:
            logging.debug("Recursive descent")
            process_files_or_directories_recursive(args.files)
        else:
            logging.debug("Single files")

            process_file_or_directory(args.files)


def set_logging_levels(verbosity: int):
    """
    Set the logging level, between 0 (critical only) to 4 (debug)

    Args:
        verbosity: The level of logging to set

    """

    if verbosity == 0:
        logging.basicConfig(level=logging.CRITICAL)
    elif verbosity == 1:
        logging.basicConfig(level=logging.ERROR)
    elif verbosity == 2:
        logging.basicConfig(level=logging.WARN)
    elif verbosity == 3:
        logging.basicConfig(level=logging.INFO)
    elif verbosity >= 4:
        logging.basicConfig(level=logging.DEBUG)

def bad_collection():
    if len(sys.argv) == 1:
        print(f"No arguments specified; specify a collection")
    else:
        print(f"Invalid collection: {sys.argv[1]}")
    print(f"Available collections: {[x for x in settings.COLLECTION_DIRS.keys()]}")
    print(f"Run {sys.argv[0]} --help for more info.")
    print("   Note: command and collection required for detailed help. e.g.:")
    print("   ./image-client.py Botany import --help")
    sys.exit(1)

if __name__ == '__main__':
    # if len(sys.argv) == 1 or sys.argv[1] not in settings.COLLECTION_DIRS.keys():
    #     bad_collection()
    args = parse_command_line()
    if args.disable_test:
        print("RUNNING IN TEST ONLY MODE. See help to disable.")

    set_logging_levels(args.verbose)

    logging.debug(f"Starting client...")


    if args.collection not in settings.COLLECTION_DIRS.keys():
        bad_collection()

    main(args)
