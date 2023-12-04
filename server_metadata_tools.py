import logging
import subprocess
import exifread


def process_exif_ring(exif_ring, path):
    """iterates through exif_ring dict keys and values to attach them to image"""
    logging.info(f"processing exif ring for filepath: {path}")
    for key, value in exif_ring.items():
        key = int(key)
        exif_attach_metadata(exif_code=key, exif_value=value, path=path)

def exif_attach_metadata(exif_code: int, exif_value, path):
    """attaches exif metadata tags to image using ExifTools subprocess in command line
    args:
        path: path to image
        exif_dict: dictionary of exif terms using exif codes, and new values to assign"""

    exif_tag = exif_code_to_tag(exif_code)
    command = ['exiftool', f"-{exif_tag}={exif_value}", path]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logging.info("exif added succesfully")


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
