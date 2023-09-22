"""unittesting for tax_assign_defitme, populate_taxon, and create_taxon functions"""
from pic_importer_test_class import TestPicturaeImporter
import unittest
import pandas as pd
from casbotany_sql_lite import sql_lite_connection
from tests.testing_tools import TestingTools
import logging
class Testtaxontrees(unittest.TestCase, TestingTools):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.md5_hash = self.generate_random_md5()
        self.logger = logging.getLogger("TestSqlInsert")
        self.connection = sql_lite_connection(db_name='casbotany_lite.db')

    def setUp(self):
        self.test_picturae_importer = TestPicturaeImporter(paths=self.md5_hash, date_string=self.md5_hash)

    def test_rankid_assign(self):
        """tests taxon_assign_defitem() function, to see that correct rankid and def_tree id are assigned"""
        tax_names = ["Castilleja miniata", "Abies balsamea subsp. balsamea", "Arabidopsis thaliana var. lyrata",
                     "Quercus robur subsp. robur subf. alba", "Rosa rugosa f. plena"]
        tax_ranks = [220, 230, 240, 270, 260]
        tax_def = [13, 14, 15, 21, 17]
        for index, tax in enumerate(tax_names):
            def_tree, rank_id = self.test_picturae_importer.taxon_assign_defitem(tax)
            self.assertEqual(def_tree, tax_def[index])
            self.assertEqual(tax_ranks, tax_def[index])

    def test_taxon_populate(self):
        """will test iterative taxon sorting function"""



