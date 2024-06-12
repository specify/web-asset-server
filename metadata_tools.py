"""metadata_tools: utility functions for the addition, removal and reading of iptc and exif image metadata"""
from timeout import timeout
import errno
import os
import logging
import subprocess
import traceback


class MetadataTools:

    @timeout(20, os.strerror(errno.ETIMEDOUT))
    def __init__(self, path):
        self.path = path
        self.logger = logging.getLogger('MetadataTools')


    def read_exif_tags(self):

        """Reads all EXIF tags from an image using ExifTool with advanced formatting and returns them as a dictionary."""
        command = ['exiftool', '-a', '-g', '-G', self.path]
        try:
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.stderr:
                raise ValueError(f"ExifTool error: {result.stderr.strip()}")
            tags = {}
            for line in result.stdout.split("\n"):
                if ": " in line:
                    group, key_value = line.split("]", 1)
                    key, value = key_value.split(":", 1)
                    formatted_group = group.replace('[', '').strip()
                    formatted_key = key.replace(' ', '').strip()
                    if value.strip():
                        tags[formatted_group + ':' + formatted_key] = value.strip()
            return tags
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"Command returned with error: {e}")
        finally:
            self.logger.info("EXIF data read successfully")

    def write_exif_tags(self, exif_dict):
        """Writes all exif tags to an image with a single call to ExifTool"""
        self.logger.info(f"Processing EXIF data for: {self.path}")
        args = ["exiftool", "-overwrite_original"]
        args.extend([f"-{key}={value}" for key, value in exif_dict.items()])
        args.append(self.path)

        try:
            subprocess.run(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            traceback.print_exc()
            raise ValueError(f"ExifTool command returned with error: {e}")
        self.logger.info("EXIF data added successfully")
