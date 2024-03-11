import unittest
import pandas as pd
import shutil
from metadata_tools import MetadataTools
class TestMetadataTools(unittest.TestCase):

    def setUp(self):
        self.path = "test.jpg"
        self.md = MetadataTools(path=self.path)
        shutil.copyfile("test.jpg", "image_backup.jpg")

    def test_is_file_larger_than(self):
        """testing file is larger than function"""
        self.assertFalse(self.md.is_file_larger_than(size_in_mb=100))
        self.assertTrue(self.md.is_file_larger_than(size_in_mb=1.5))
        self.assertFalse(self.md.is_file_larger_than(size_in_mb=5))

    def test_code_to_tag(self):
        """tests code to tag converter function"""
        self.assertTrue(self.md.exif_code_to_tag(271), 'Make')
        self.assertTrue(self.md.exif_code_to_tag(33432), 'Copyright')
        self.assertTrue(self.md.exif_code_to_tag(315), 'Artist')


    def test_iptc_read(self):
        """testing iptc read function"""
        iptc_dict = self.md.read_iptc_metadata()
        self.assertFalse(pd.isna(iptc_dict))
        self.assertNotEqual(iptc_dict, {})
        self.assertEqual(iptc_dict['contact'], [])

    def test_IPTC_attach(self):
        """testing decode_exif_data function"""
        self.md.iptc_attach_metadata(iptc_field='by-line', iptc_value="Mateo De La Roca")
        self.md.iptc_attach_metadata(iptc_field='copyright notice', iptc_value="@CopyrightIPTC")
        self.md.iptc_attach_metadata(iptc_field='caption/abstract',
                                     iptc_value="An upsidedown image of a woodworking shop")
        iptc_dict = self.md.read_iptc_metadata()
        self.assertEqual(b"@CopyrightIPTC", iptc_dict['copyright notice'])
        self.assertEqual(b"Mateo De La Roca", iptc_dict['by-line'])
        self.assertEqual(b"An upsidedown image of a woodworking shop", iptc_dict['caption/abstract'])
    def test_exif_read(self):
        """tests exif read function"""
        exif_dict = self.md.read_exif_metadata(convert_tags=False)
        self.assertFalse(pd.isna(exif_dict))
        self.assertNotEqual(exif_dict, {})
        self.assertEqual(exif_dict[272], 'iPhone XR')

    def test_exif_attach(self):
        """tests exif attach function"""
        self.md.exif_attach_metadata(exif_code=271, exif_value="Samsung")
        self.md.exif_attach_metadata(exif_code=305, exif_value="15.2.3")
        self.md.exif_attach_metadata(exif_code=274, exif_value=3)

        exif_dict = self.md.read_exif_metadata(convert_tags=True)
        self.assertEqual("Samsung", exif_dict['Make'])
        self.assertEqual("15.2.3", exif_dict['Software'])
        self.assertEqual(3, exif_dict['Orientation'])

    def test_iptc_exif_overwrite(self):
        """tests that a given iptc variable is not overwritten
           by writing to exif and vice versa
        """
        self.md.exif_attach_metadata(exif_code=33432, exif_value="CalAcademy")
        self.md.iptc_attach_metadata(iptc_field='copyright notice', iptc_value="CalAcademy2")
        exif_dict = self.md.read_exif_metadata(convert_tags=False)

        self.assertEqual(exif_dict[33432], "CalAcademy")
        self.md.exif_attach_metadata(exif_code=33432, exif_value="CalAcademy")
        iptc_dict = self.md.read_iptc_metadata()
        self.assertEqual(b"CalAcademy2", iptc_dict['copyright notice'])


    def tearDown(self):
        del self.md
        shutil.copyfile("image_backup.jpg", "test.jpg")


