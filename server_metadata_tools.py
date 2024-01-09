import logging
import subprocess
import exifread
import traceback

def process_exif_ring(exif_ring: dict, path: str):
    """iterates through exif_ring dict keys and values to attach them to image"""
    logging.info(f"processing exif ring for filepath: {path}")
    for key, value in exif_ring.items():
        key = key
        exif_attach_metadata(exif_code=key, exif_value=value, path=path)

def exif_attach_metadata(exif_code, exif_value, path):
    """attaches exif metadata tags to image using ExifTools subprocess in command line
    args:
        path: path to image
        exif_dict: dictionary of exif terms using exif codes, and new values to assign"""


    exif_tag = exif_code_to_tag(exif_code)

    command = ['exiftool', f"-{exif_tag}={exif_value}", '-overwrite_original', f'{path}']
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except Exception as e:
        traceback.print_exc()
        raise ValueError(f"command return with error  {e}")

    logging.info(f"exif {command} added succesfully")


def exif_code_to_tag(exif_code):
    """converts exif code into the string of the tag name
        args:
            exif_code: the integer code of an exif tag to convert to TAG"""
    exif_code = int(exif_code)
    tag_name = exifread.tags.EXIF_TAGS.get(exif_code, "Unknown Tag")

    if tag_name == "Unknown Tag":
        raise ValueError("unknown code")
    else:
        return tag_name[0]
