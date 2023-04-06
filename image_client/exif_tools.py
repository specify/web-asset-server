from PIL import Image
from timeout import timeout
import errno
import os
import iz_importer_config
import re
import logging


class ExifTools:

    # Hangs on some files, don't know why, needs to be killed
    @timeout(20, os.strerror(errno.ETIMEDOUT))
    def __init__(self, full_path):
        self.decoded_exif_data = {}
        self.copyright = None
        self.casiz_number = None

        self.logger = logging.getLogger('Client.ExifTools')

        self.logger.setLevel(logging.DEBUG)

        self.full_path = full_path
        print(f"        Extracting exif: {full_path}")
        if self.is_file_larger_than(full_path,100):
            print("Larger than 100M, skipping EXIF extraction")
        self.raw_exif_data = Image.open(full_path).getexif()
        self.decode_exif_data()
        self.process_casiz_elements()


    def is_file_larger_than(self,filepath: str, size_in_mb) -> bool:
        """
        Check if a file at the given filepath is larger than the specified size (in megabytes).
        """
        # Get the size of the file in bytes
        size_in_bytes = os.path.getsize(filepath)

        # Convert the size to megabytes
        size_in_mb_actual = size_in_bytes / (1024 * 1024)

        # Compare the actual size with the specified size
        return size_in_mb_actual > size_in_mb

    def decode_exif_data(self):

        # print("processing exif data")
        for key, value in self.raw_exif_data.items():
            # print(f"Processing {key}:{value}")
            if key in iz_importer_config.EXIF_DECODER_RING.keys():
                print(f"  {iz_importer_config.EXIF_DECODER_RING[key]}: {value}")
                self.decoded_exif_data[iz_importer_config.EXIF_DECODER_RING[key]] = value

    def process_casiz_elements(self):
        self.extract_casiz_number()
        self.extract_casiz_copyright()

    def extract_casiz_number(self):
        if "ImageDescription" in self.decoded_exif_data.keys():
            image_description = self.decoded_exif_data['ImageDescription']
            ints = re.findall(r'\d+', image_description)
            if len(ints) == 0:
                self.logger.debug(f" Can't find any id number in the image description: {image_description}")

            else:
                if len(ints[0]) >= iz_importer_config.MINIMUM_ID_DIGITS:
                    casiz_number = int(ints[0])
                    self.casiz_number = casiz_number
                    return

    def extract_casiz_copyright(self):
        if 'Copyright' not in self.decoded_exif_data.keys():
            return
        self.copyright = self.decoded_exif_data['Copyright']
        if self.copyright is not None:
            if self.copyright.startswith('Â'):
                self.copyright = self.copyright[1:]
            #     Common data errors
            if len(self.copyright) <= 2:
                return
            if "\x00\x00\x00\x00\x00\x00\x00" in self.copyright:
                self.copyright = None

