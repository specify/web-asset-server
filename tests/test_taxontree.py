"""unittesting for tax_assign_defitme, populate_taxon, and create_taxon functions"""
import shutil
from tests.pic_importer_test_class import TestPicturaeImporter
import unittest
from image_client.casbotany_sql_lite import sql_lite_connection
from tests.testing_tools import TestingTools
import logging
from image_client.picturae_import_utils import unique_ordered_list
import pandas as pd
import os
from uuid import uuid4
os.chdir("./image_client")
class Testtaxontrees(unittest.TestCase, TestingTools):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.md5_hash = self.generate_random_md5()
        self.logger = logging.getLogger("TestSqlInsert")
        self.connection = sql_lite_connection('../tests/casbotany_lite.db')
        self.taxon_dicts = []
    def setUp(self):
        self.test_picturae_importer = TestPicturaeImporter(paths=self.md5_hash, date_string=self.md5_hash)
        # creating restore point for db
        shutil.copyfile("../tests/casbotany_lite.db", "../tests/casbotany_backup.db")

        self.taxon_dicts = [{"full_name": "Castilleja miniata subsp. fakus var. fake x cool",
                             "gen_spec": "Castilleja miniata", "first_intra": "Castilleja miniata subsp. fakus",
                             "genus": "Castilleja", "family_name": "Orobanchaceae"},
                            {"full_name": "Rafflesia arnoldi var. summi",
                             "gen_spec": "Rafflesia arnoldi", "first_intra": "Rafflesia arnoldi var. summi",
                             "genus": "Rafflesia", "family_name": "Rafflesiaceae"},
                            {"full_name": "Salix x ambigua",
                             "gen_spec": "Salix x ambigua", "first_intra": "Salix x ambigua",
                             "genus": "Salix", "family_name": "Salicaceae"}
                           ]

    def test_rankid_assign(self):
        """tests taxon_assign_defitem() function, to see that correct rankid and def_tree id are assigned"""
        tax_names = ["Castilleja miniata", "Abies balsamea subsp. balsamea", "Arabidopsis thaliana var. lyrata",
                     "Quercus robur subsp. robur subf. alba", "Rosa rugosa f. plena"]
        tax_ranks = [220, 230, 240, 270, 260]
        tax_def = [13, 14, 15, 21, 17]
        for index, tax in enumerate(tax_names):
            def_tree, rank_id = self.test_picturae_importer.taxon_assign_defitem(tax)
            self.assertEqual(def_tree, tax_def[index])
            self.assertEqual(rank_id, tax_ranks[index])

    def test_populate_taxon(self):
        """will test iterative taxon sorting function"""
        new_taxa_lists = [["Castilleja miniata subsp. fakus var. fake x cool", "Castilleja miniata subsp. fakus"],
                          ["Rafflesia arnoldi var. summi", "Rafflesia arnoldi"],
                          ["Salix x ambigua"]]
        for index, tax_dict in enumerate(self.taxon_dicts):
            self.test_picturae_importer.taxon_list = []
            self.test_picturae_importer.full_name = tax_dict["full_name"]
            self.test_picturae_importer.gen_spec = tax_dict["gen_spec"]
            self.test_picturae_importer.first_intra = tax_dict["first_intra"]
            self.test_picturae_importer.genus = tax_dict["genus"]

            self.test_picturae_importer.populate_taxon()

            self.assertEqual(self.test_picturae_importer.taxon_list, new_taxa_lists[index])

    # this can be rewritten to test an iterative set, need to ask some questions about sqlite parameters
    # on frontend
    # I don't consider this to be a very good test-set, I'll have to revise this section
    def test_generate_taxon_fields(self):
        """tests that generate taxon fields assigns the expected values to each field"""
        self.test_picturae_importer.taxon_list = []
        self.test_picturae_importer.is_hybrid = True
        # self.test_picturae_importer.taxon_guid = uuid4()
        self.test_picturae_importer.family_name = "Salicaceae"
        self.test_picturae_importer.full_name = "Salix x ambigua"
        self.test_picturae_importer.gen_spec = "Salix x ambigua"
        self.test_picturae_importer.first_intra = "Salix x ambigua"
        self.test_picturae_importer.genus = "Salix"
        self.test_picturae_importer.tax_name = "x ambigua"

        self.test_picturae_importer.populate_taxon()

        self.test_picturae_importer.author = "Ehrh."
        self.test_picturae_importer.taxon_guid = uuid4()

        self.test_picturae_importer.parent_list = [self.test_picturae_importer.full_name,
                                                   self.test_picturae_importer.first_intra,
                                                   self.test_picturae_importer.gen_spec,
                                                   self.test_picturae_importer.genus,
                                                   self.test_picturae_importer.family_name]

        self.test_picturae_importer.parent_list = unique_ordered_list(self.test_picturae_importer.parent_list)

        self.assertEqual(self.test_picturae_importer.parent_list, ['Salix x ambigua', 'Salix', 'Salicaceae'])

        self.assertEqual(self.test_picturae_importer.parent_list[1], 'Salix')

        author_insert, tree_item_id, \
        rank_end, parent_id, taxon_guid = self.test_picturae_importer.generate_taxon_fields(index=0, taxon="Salix x ambigua")
        print(f"sample it:{author_insert}")
        self.assertTrue(pd.isna(author_insert))
        self.assertEqual(parent_id, 21855)
        self.assertEqual(tree_item_id, 13)
        self.assertEqual(rank_end, "x ambigua")



    def tearDown(self):
        del self.test_picturae_importer
        # restoring db to original state removing backup
        shutil.copyfile("../tests/casbotany_backup.db", "../tests/casbotany_lite.db")
        os.remove("../tests/casbotany_backup.db")


if __name__ == '__main__':
    unittest.main()