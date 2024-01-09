import pandas as pd

import settings
import pytest
import filecmp
import requests
from uuid import uuid4
from os.path import splitext
import json
import os
from datetime import datetime
import pytz
from client_utilities import update_time_delta
from client_utilities import build_url
from client_utilities import generate_token
from client_utilities import get_timestamp
from collection_definitions import COLLECTION_DIRS
from image_db import TIME_FORMAT_NO_OFFESET
import hashlib
import time

def get_file_md5(filename):
    with open(filename, 'rb') as f:
        md5_hash = hashlib.md5()
        while chunk := f.read(8192):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

attach_loc = "None"
TEST_JPG = "test.jpg"
TEST_PATH = "/foo/bar/baz"
TEST_NOTES = "alskeifhjais78yas8efhaisef87yaihrti478yfhudyhdrsifslfdhiju"
dt, tz = '2020-01-01 00:00:01 UTC'.rsplit(maxsplit=1)

dto = datetime.strptime(dt, '%Y-%m-%d %H:%M:%S').replace(tzinfo=pytz.timezone(tz))

TEST_DATE = dto

EXIF_DECODER_RING = {
      "33432": "\u00A9 california academy of sciences",
        "315": "Claude Monet",
        "33437": "3/2"

}

@pytest.fixture(scope='function', autouse=True)
def test_teardown(request):
    try:
        delete_attach_loc()
    except:
        pass


def setup_module():
    update_time_delta()


def test_root():
    body = "Specify attachment server"
    response = requests.get(build_url(""))
    assert response.status_code == 200
    result = response.content.decode("utf-8")
    assert body == result


def test_web_asset_store():
    body = f"""<?xml version="1.0" encoding="UTF-8"?>
<urls>
    <url type="read"><![CDATA[http://{settings.SERVER_NAME}:{settings.SERVER_PORT}/fileget]]></url>
    <url type="write"><![CDATA[http://{settings.SERVER_NAME}:{settings.SERVER_PORT}/fileupload]]></url>
    <url type="delete"><![CDATA[http://{settings.SERVER_NAME}:{settings.SERVER_PORT}/filedelete]]></url>
    <url type="getmetadata"><![CDATA[http://{settings.SERVER_NAME}:{settings.SERVER_PORT}/getmetadata]]></url>
    <url type="testkey">http://{settings.SERVER_NAME}:{settings.SERVER_PORT}/testkey</url>
</urls>
"""
    endpoint = "web_asset_store.xml"
    response = requests.get(build_url(endpoint))
    assert response.status_code == 200
    result = response.content.decode("utf-8")
    assert body == result


def test_testkey():
    random = str(uuid4())
    token = generate_token(get_timestamp(), random)
    r = requests.get(build_url("testkey"),
                     params={'random': random, 'token': token})

    assert r.status_code == 200


def post_test_file(supplementary_data={}, uuid_override=None, md5=False):
    global attach_loc
    local_filename = TEST_JPG
    if uuid_override is not None:
        uuid = uuid_override
    else:
        uuid = str(uuid4())
    name, extension = splitext(local_filename)
    attach_loc = uuid + extension


    data = {
        'store': attach_loc,
        'type': 'image',
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc),
        'original_filename': local_filename
    }
    if md5:
        md5 = get_file_md5(TEST_JPG)
        data['orig_md5']= md5
    merged_data = z = {**data, **supplementary_data}

    files = {
        'image': (attach_loc, open(local_filename, 'rb')),
    }

    r = requests.post(build_url("fileupload"), files=files, data=merged_data)
    return r


def get_exif_data():
    """used to read test exif data from image on server"""
    get_exif_params = {
                        'filename': attach_loc,
                        'datatype': 'image',
                        'coll': list(COLLECTION_DIRS.keys())[0],
                        'token': generate_token(get_timestamp(), attach_loc)
                    }

    r = requests.get(build_url("getmetadata"), params=get_exif_params)

    exif_data = json.loads(r.text)

    return exif_data



@pytest.mark.dependency()
def test_file_post():
    r = post_test_file()
    assert r.status_code == 200
    r = delete_attach_loc()
    assert r.status_code == 200

@pytest.mark.dependency()
def test_md5_round_trip():
    r = post_test_file(md5=True)
    md5 = get_file_md5(TEST_JPG)

    assert r.status_code == 200
    params = {
        'file_string': md5,
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), md5),
        'search_type': 'md5'
    }

    r = requests.get(build_url("getImageRecord"), params=params)
    assert r.status_code == 200

    data = json.loads(r.text)
    assert data[-1]['orig_md5'] == md5

    r = delete_attach_loc()
    assert r.status_code == 200


@pytest.mark.dependency()
def test_file_get():
    r = post_test_file()
    assert r.status_code == 200

    image_filename = 'response.jpg'

    params = {
        'filename': attach_loc,
        'type': 'image',
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc)
    }

    r = requests.get(build_url("fileget"), params=params)

    assert r.status_code == 200
    with open(image_filename, 'wb') as f:
        f.write(r.content)
    assert filecmp.cmp(image_filename, TEST_JPG)
    os.remove(image_filename)
    r = delete_attach_loc()
    assert r.status_code == 200


def test_update_metadata():
    r = post_test_file()

    assert r.status_code == 200

    exif_data = get_exif_data()
    # checking field not present before function execution

    assert 'Copyright' not in exif_data[0]['Fields']

    assert 'Artist' not in exif_data[0]['Fields']

    assert exif_data[2]['Fields']['FNumber'] == "9/5"

    # updating exif data
    data = {'filename': attach_loc,
            'coll': list(COLLECTION_DIRS.keys())[0],
            'token': generate_token(get_timestamp(), attach_loc),
            'exif_ring': json.dumps(EXIF_DECODER_RING)
    }

    url = build_url('updatemetadata')

    r = requests.post(url=url, data=data)

    assert r.status_code == 200

    exif_data = get_exif_data()

    # checking fields present after function execution

    assert exif_data[0]['Fields']['Copyright'] == "\u00A9 california academy of sciences"

    assert exif_data[0]['Fields']['Artist'] == "Claude Monet"

    assert exif_data[2]['Fields']['FNumber'] == "3/2"

    r = delete_attach_loc()

    assert r.status_code == 200


@pytest.mark.dependency()
def test_file_get_no_key():
    r = post_test_file()
    assert r.status_code == 200

    image_filename = 'response.jpg'

    params = {
        'filename': attach_loc,
        'type': 'image',
        'coll': list(COLLECTION_DIRS.keys())[0],
        'original_filename': TEST_JPG
    }

    r = requests.get(build_url("fileget"), params=params)

    assert r.status_code == 200
    with open(image_filename, 'wb') as f:
        f.write(r.content)
    assert filecmp.cmp(image_filename, TEST_JPG)
    os.remove(image_filename)

    r = delete_attach_loc()

    assert r.status_code == 200


@pytest.mark.dependency(depends=['test_file_post'])
def test_thumbnail_get():
    r = post_test_file()
    assert r.status_code == 200

    thumb_filename = 'response.thumb.jpg'
    params = {
        'filename': attach_loc,
        'type': 'T',
        'scale': 100,
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc)
    }

    r = requests.get(build_url("fileget"), params=params)

    assert r.status_code == 200
    with open(thumb_filename, 'wb') as f:
        f.write(r.content)
    assert not filecmp.cmp(thumb_filename, TEST_JPG)
    os.remove(thumb_filename)

    r = delete_attach_loc()

    assert r.status_code == 200


@pytest.mark.dependency(depends=['test_file_post'])
def test_get_static_url():
    r = post_test_file()

    assert r.status_code == 200

    params = {
        'filename': attach_loc,
        'type': 'image',
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc)
    }

    r = requests.get(build_url("getfileref"), params=params)
    url = r.text;
    assert r.status_code == 200
    # print(f"Got URL: {url}")
    r = requests.get(url)
    assert r.status_code == 200

    r = delete_attach_loc()
    assert r.status_code == 200


@pytest.mark.dependency(depends=['test_file_post'])
def test_get_exif():

    r = post_test_file()

    assert r.status_code == 200

    params = {
        'filename': attach_loc,
        'datatype': 'image',
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc)
    }

    r = requests.get(build_url("getmetadata"), params=params)
    assert r.status_code == 200

    exif_data = json.loads(r.text)
    assert exif_data[0]['Fields']['Model'] == "iPhone XR"

    r = delete_attach_loc()

    assert r.status_code == 200


@pytest.mark.dependency(depends=['test_file_post'])
def test_delete_file():
    r = post_test_file()

    assert r.status_code == 200

    data = {
        'filename': attach_loc,
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc),
        'original_filename': TEST_JPG
    }

    r = requests.post(build_url("filedelete"), data=data)

    assert r.status_code == 200


@pytest.mark.dependency(depends=['test_delete_file'])
def test_get_after_delete():
    params = {
        'filename': attach_loc,
        'type': 'image',
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc)
    }

    r = requests.get(build_url("fileget"), params=params)

    assert r.status_code == 404


@pytest.mark.dependency(depends=['test_delete_file'])
def test_thumbnail_get_after_delete():
    params = {
        'filename': attach_loc,
        'type': 'T',
        'scale': 100,
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc)
    }

    r = requests.get(build_url("fileget"), params=params)

    assert r.status_code == 404


def post_with_metadata(redacted=True, uuid_override=None):
    global attach_loc
    local_filename = TEST_JPG
    if uuid_override is None:
        uuid = str(uuid4())
    else:
        uuid = uuid_override
    name, extension = splitext(local_filename)
    attach_loc = uuid + extension

    data = {
        'store': attach_loc,
        'type': 'image',
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc),
        'original_filename': local_filename,
        'original_path': TEST_PATH,
        'redacted': redacted,
        'notes': TEST_NOTES,
        'datetime': TEST_DATE
    }
    files = {
        'image': (attach_loc, open(local_filename, 'rb')),
    }

    r = requests.post(build_url("fileupload"), files=files, data=data)
    return r


def delete_attach_loc():
    data = {
        'filename': attach_loc,
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc),
        'original_filename': TEST_JPG
    }

    r = requests.post(build_url("filedelete"), data=data)

    return r


@pytest.mark.dependency(depends=['test_delete_file'])
def test_file_post_with_metadata():
    r = post_with_metadata()

    assert r.status_code == 200

    r = delete_attach_loc()
    assert r.status_code == 200


@pytest.mark.dependency()
def test_get_redacted_image_by_original_filename():
    global attach_loc
    r = post_with_metadata(redacted=True)
    assert r.status_code == 200

    params = {
        'file_string': TEST_JPG,
        'coll': list(COLLECTION_DIRS.keys())[0],
        'exact': True,
        'token': generate_token(get_timestamp(), TEST_JPG),
        'search_type': 'filename'
    }

    r = requests.get(build_url("getImageRecord"), params=params)
    assert r.status_code == 200

    data = json.loads(r.text)
    assert data[-1]['original_filename'] == TEST_JPG
    assert data[-1]['original_path'] == TEST_PATH
    assert data[-1]['notes'] == TEST_NOTES
    assert data[-1]['redacted']
    assert pytz.utc.localize(datetime.strptime(data[-1]['datetime'], TIME_FORMAT_NO_OFFESET)) == TEST_DATE

    r = delete_attach_loc()
    assert r.status_code == 200


@pytest.mark.dependency()
def test_get_non_redacted_image_by_original_filename():
    global attach_loc
    r = post_with_metadata(redacted=False)
    assert r.status_code == 200

    params = {
        'file_string': TEST_JPG,
        'token': generate_token(get_timestamp(), TEST_JPG),
        'search_type': 'filename',
    }

    r = requests.get(build_url("getImageRecord"), params=params)
    assert r.status_code == 200

    data = json.loads(r.text)
    assert data[-1]['original_filename'] == TEST_JPG
    assert data[-1]['original_path'] == TEST_PATH
    assert data[-1]['notes'] == TEST_NOTES
    assert data[-1]['redacted'] == False
    assert pytz.utc.localize(datetime.strptime(data[-1]['datetime'], TIME_FORMAT_NO_OFFESET)) == TEST_DATE

    r = delete_attach_loc()
    assert r.status_code == 200


def test_file_get_redacted_cases():
    # test it with static url
    global attach_loc
    r = post_with_metadata(redacted=True)
    assert r.status_code == 200

    params = {
        'filename': attach_loc,
        'type': 'image',
        'coll': list(COLLECTION_DIRS.keys())[0],
    }

    r = requests.get(build_url("fileget"), params=params)
    assert r.status_code != 200

    params = {
        'filename': attach_loc,
        'type': 'image',
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc)
    }
    r = requests.get(build_url("fileget"), params=params)
    assert r.status_code == 200

    r = delete_attach_loc()
    assert r.status_code == 200
    r = post_with_metadata(redacted=False)
    assert r.status_code == 200

    params = {
        'filename': attach_loc,
        'type': 'image',
        'coll': list(COLLECTION_DIRS.keys())[0],
    }
    r = requests.get(build_url("fileget"), params=params)

    assert r.status_code == 200
    r = delete_attach_loc()
    assert r.status_code == 200


def test_name_collision_failure():
    uuid = str(uuid4())

    r = post_test_file(uuid_override=uuid)
    assert r.status_code == 200

    r = post_test_file(uuid_override=uuid)
    assert r.status_code == 409

    r = delete_attach_loc()
    assert r.status_code == 200


def test_duplicate_basename_failure():
    global attach_loc

    uuid = str(uuid4())

    r = post_test_file(uuid_override=uuid)
    assert r.status_code == 200

    attach_loc = "test_string"

    r = post_test_file(uuid_override=uuid)
    assert r.status_code == 409

    r = delete_attach_loc()
    assert r.status_code == 200

    attach_loc = "None"



def test_static_redacted():
    global attach_loc
    r = post_with_metadata(redacted=True)
    assert r.status_code == 200
    params = {
        'filename': attach_loc,
        'type': 'image',
        'coll': list(COLLECTION_DIRS.keys())[0],
        'token': generate_token(get_timestamp(), attach_loc)
    }

    r = requests.get(build_url("getfileref"), params=params)
    url = r.text;

    assert r.status_code == 200
    r = requests.get(url)
    assert r.status_code == 403

    r = delete_attach_loc()
    assert r.status_code == 200


def test_store_shortname():
    uuid = "sh"
    r = post_test_file(uuid_override=uuid)
    assert r.status_code == 400

