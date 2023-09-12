import requests, hmac
import time
import sys
import server_host_settings
from uuid import uuid4
from os.path import splitext
import datetime
import logging
import os

TIME_FORMAT = "%Y-%m-%d %H:%M:%S%z"


class UploadFailureException(Exception):
    pass


class DeleteFailureException(Exception):
    pass


class FileNotFoundException(Exception):
    pass


class ImageClient:
    def __init__(self):
        self.datetime_now = datetime.datetime.now(datetime.timezone.utc)
        self.update_time_delta()

    def split_filepath(self, filepath):
        cur_filename = os.path.basename(filepath)
        cur_file_ext = cur_filename.split(".")[-1]
        return cur_filename, cur_file_ext

    def build_url(self, endpoint):
        host = server_host_settings.SERVER_NAME
        port = server_host_settings.SERVER_PORT
        return f"http://{host}:{port}/{endpoint}"

    def update_time_delta_from_response(self, response):
        global server_time_delta
        try:
            timestamp = response.headers['X-Timestamp']
        except KeyError:
            server_time_delta = 0
            return

        server_time_delta = int(timestamp) - int(time.time())
        print(f"Updated server time delta to {server_time_delta}")

    def get_timestamp(self):
        """Return an integer timestamp with one second resolution for
        the current moment.
        """
        return int(time.time()) + server_time_delta

    def update_time_delta(self):
        response = requests.get(self.build_url(""))
        self.update_time_delta_from_response(response)

    def generate_token(self, filename):
        """Generate the auth token for the given filename and timestamp. """
        timestamp = self.get_timestamp()
        msg = str(timestamp).encode() + filename.encode()
        mac = hmac.new(server_host_settings.SERVER_KEY.encode(), msg=msg, digestmod='md5')
        return ':'.join((mac.hexdigest(), str(timestamp)))

    def delete_from_image_server(self, attach_loc, collection):
        data = {
            'filename': attach_loc,
            'coll': collection,
            'token': self.generate_token(attach_loc),
        }
        url = self.build_url("filedelete")
        logging.debug(f"Deleting {url} from server")
        r = requests.post(url, data=data)
        if r.status_code == 404:
            raise FileNotFoundException
        if r.status_code != 200:
            print(f"Deletion failed, aborted: {r.status_code}:{r.text}")
            raise DeleteFailureException

    def upload_to_image_server(self, full_path, redacted, collection, original_path=None):
        if full_path is None or redacted is None or collection is None:
            errstring = f"Bad input falues to upload to image server: {full_path} {redacted} {collection}"
            print(errstring, file=sys.stderr, flush=True)
            raise UploadFailureException(errstring)
        local_filename = full_path
        uuid = str(uuid4())
        extension = local_filename.split(".")[-1]
        attach_loc = uuid + "." + extension
        if original_path is not None:
            upload_path = original_path
        else:
            upload_path = full_path
        data = {
            'store': attach_loc,
            'type': 'image',
            'coll': collection,
            'token': self.generate_token(attach_loc),
            'original_filename': os.path.basename(local_filename),
            'original_path': upload_path,
            'redacted': str(redacted),
            'notes': None,
            'datetime': self.datetime_now.strftime(TIME_FORMAT)
        }

        files = {
            'image': (attach_loc, open(local_filename, 'rb')),
        }
        url = self.build_url("fileupload")
        logging.debug(f"Attempting upload to {url}")
        r = requests.post(url, files=files, data=data)
        if r.status_code != 200:
            print(f"Image upload aborted: {r.status_code}:{r.text}")
            raise UploadFailureException
        else:
            params = {
                'filename': attach_loc,
                'coll': collection,
                'type': 'image',
                'token': self.generate_token(attach_loc)
            }

            r = requests.get(self.build_url("getfileref"), params=params)
            url = r.text
            assert r.status_code == 200

            print(f"  Uploaded: {local_filename},{attach_loc},{url}", flush=True)
        logging.debug("Upload to file server complete")

        return url, attach_loc

    # works for just basename +ext. "exact" does a sql "like" operation
    def check_image_db_if_filename_imported(self, collection, filename, exact=False):
        params = {
            'file_string': filename,
            'coll': collection,
            'exact': exact,
            'search_type': 'filename',
            'token': self.generate_token(filename)
        }
        return self.decode_response(params)

    # works for full filepath and original extension. "exact" does a sql "like" operation
    def check_image_db_if_filepath_imported(self, collection, filepath, exact=False):
        params = {
            'file_string': filepath,
            'coll': collection,
            'exact': exact,
            'search_type': 'path',
            'token': self.generate_token(filepath)
        }
        return self.decode_response(params)

    def check_specify_if_filepath_attached_to_collection_object_id(self,collection,filepath,collection_object_id):
        pass


    def decode_response(self,params):
        r = requests.get(self.build_url("getImageRecord"), params=params)
        if r.status_code == 404:
            logging.debug(f"Checked {params['file_string']} and found no duplicates")
            return False
        if r.status_code == 200:
            logging.debug(f"Checked {params['file_string']} - already imported")
            return True
        if r.status_code == 500:
            logging.error(f"500: Internal server error checking {params['file_string']}")
            assert False

        assert False