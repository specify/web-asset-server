#!/usr/bin/env python3
from bottle import route, run

import logging
from collections import defaultdict, OrderedDict
from functools import wraps
from glob import glob
from mimetypes import guess_type
from os import makedirs, path, remove
from distutils.util import strtobool
from urllib.parse import quote
from urllib.request import pathname2url
import exifread
import traceback
import hmac
import json
import time
from collection_definitions import COLLECTION_DIRS
from datetime import datetime
from time import sleep
from metadata_tools import MetadataTools
from sh import convert
from bottle import Bottle
from image_db import ImageDb
from image_db import TIME_FORMAT

app = application = Bottle()
import settings

level = logging.getLevelName(settings.LOG_LEVEL)
logging.basicConfig(filename='app.log', level=level)


from bottle import (
    Response, request, response, static_file, template, abort,
    HTTPResponse)


def get_image_db():
    image_db = ImageDb()
    return image_db
#
# @route('/')
# def index():
#     return 'This is the homepage'

@app.route('/')
def main_page():
    log("Hit root")
    return 'Specify attachment server'

# run(host='0.0.0.0', port=8080)
def log(msg):
    logging.debug(msg)
def get_image_db():
    image_db = ImageDb()
    return image_db

if __name__ == '__main__':
    from bottle import run
    image_db = get_image_db()
    log("Starting up....")
    image_db = ImageDb()
    while image_db.connect() is not True:
        sleep(5)
        log("Retrying db connection....")
    image_db.create_tables()
    log("running server...")

    run(host='0.0.0.0',
        # app=app, #this is the line
        port=8081,
        server=settings.SERVER,
        debug=settings.DEBUG_APP,
        reloader=settings.DEBUG_APP)

    log("Exiting.")