"""unittesting for tax_assign_defitem, populate_taxon, and create_taxon functions"""
import unittest
import os
import shutil
import logging
import pandas as pd
from uuid import uuid4
from image_client import time_utils
from image_client.picturae_import_utils import remove_two_index
from tests.pic_importer_test_class_lite import TestPicturaeImporterlite
from tests.testing_tools import TestingTools
from image_client.picturae_import_utils import unique_ordered_list
os.chdir("./image_client")
class Testtaxontrees(unittest.TestCase, TestingTools):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.md5_hash = self.generate_random_md5()
        self.logger = logging.getLogger("TestSqlInsert")
        self.taxon_dicts = []


    def setUp(self):
        self.test_picturae_importer_lite = TestPicturaeImporterlite(paths=self.md5_hash, date_string=self.md5_hash)

        self.sql_csv_tools = self.test_picturae_importer_lite.sql_csv_tools

        # creating restore point for db
        shutil.copyfile("../tests/casbotany_lite.db", "../tests/casbotany_backup.db")




        data = {'CatalogNumber': ["12345", "12346", "12347", "12348"],
                'verbatim_date': ['May 5 , 1955', 'May 20 , 1980', 'March 20th, 1925', 'April 5th, 2008'],
                'start_date': ['5/05/1955', '5/20/1980', '3/20/1925', '4/05/2008'],
                'end_date': ['5/05/1955', '5/20/1980', '3/20/1925', '4/05/2008'],
                'collector_number': ['123456', '123455', '123454', '123453'],
                'locality': ['place1', 'place2', 'place3', 'place4'],
                'fullname': ['Castilleja miniata', 'Castilleja miniata subsp. fakus var. fake x cool',
                             'Rafflesia arnoldi var. summi', 'Salix x ambigua'],
                'Genus': ['Castilleja', 'Castilleja', 'Rafflesia', 'Salix'],
                'taxname': ['miniata', 'fake x cool', 'summi', 'x ambigua'],
                'gen_spec': ['Castilleja miniata', 'Castilleja miniata', 'Rafflesia arnoldi', 'Salix x ambigua'],
                'first_intra': ['Castilleja miniata', 'Castilleja miniata subsp. fakus',
                                'Rafflesia arnoldi var. summi', 'Salix x ambigua'],
                'country': ['United States', 'United States', 'United States', 'United States'],
                'state': ['California', 'California', 'California', 'California'],
                'county': ['Marin', 'Marin', 'Marin', 'Marin'],
                'qualifier': [pd.NA, pd.NA, pd.NA, pd.NA],
                'name_matched': ['Castilleja miniata', 'Castilleja miniata subsp. fakus var. fake x cool',
                             'Rafflesia arnoldi var. summi', 'Salix x ambigua'],
                'Family': ['Orobanchaceae', 'Orobanchaceae', 'Rafflesiaceae', 'Salicaceae'],
                'Hybrid': [False, True, False, True],
                'accepted_author': ['Dougl. ex Hook.', 'Erd.', 'Drew', 'Schleich. ex Ser']
                }
        self.test_picturae_importer_lite.record_full = pd.DataFrame(data)


    def test_rankid_assign(self):
        """tests taxon_assign_defitem() function, to see that correct rankid and def_tree id are assigned"""
        tax_names = ["Castilleja miniata", "Abies balsamea subsp. balsamea", "Arabidopsis thaliana var. lyrata",
                     "Quercus robur subsp. robur subf. alba", "Rosa rugosa f. plena"]
        tax_ranks = [220, 230, 240, 270, 260]
        tax_def = [13, 14, 15, 21, 17]
        for index, tax in enumerate(tax_names):
            def_tree, rank_id = self.test_picturae_importer_lite.taxon_assign_defitem(tax)
            self.assertEqual(def_tree, tax_def[index])
            self.assertEqual(rank_id, tax_ranks[index])

    def test_populate_taxon(self):
        """will test iterative taxon sorting function"""
        tax_names = [[],
                     ["Castilleja miniata subsp. fakus var. fake x cool", "Castilleja miniata subsp. fakus"],
                     ["Rafflesia arnoldi var. summi", "Rafflesia arnoldi"],
                     ["Salix x ambigua"]]

        for index, row in self.test_picturae_importer_lite.record_full.iterrows():
            self.test_picturae_importer_lite.populate_fields(row)

            self.test_picturae_importer_lite.populate_taxon()

            self.assertEqual(self.test_picturae_importer_lite.taxon_list, tax_names[index])


    def test_generate_taxon_fields(self):
        """tests that generate taxon fields assigns the expected values to each field"""

        # test lists of expected order of ranks, and names
        # order set as taxon added highest to lowest rank
        rank_list = [230, 240, 220, 240, 220]
        tax_ends = ["fakus", "fake x cool", "arnoldi", "summi", "x ambigua"]
        rank_num = 0
        for index, row in self.test_picturae_importer_lite.record_full.iterrows():
            self.test_picturae_importer_lite.populate_fields(row)

            self.test_picturae_importer_lite.taxon_list = []

            self.test_picturae_importer_lite.populate_taxon()


            self.test_picturae_importer_lite.taxon_guid = uuid4()

            self.test_picturae_importer_lite.parent_list = [self.test_picturae_importer_lite.full_name,
                                                            self.test_picturae_importer_lite.first_intra,
                                                            self.test_picturae_importer_lite.gen_spec,
                                                            self.test_picturae_importer_lite.genus,
                                                            self.test_picturae_importer_lite.family_name]

            self.test_picturae_importer_lite.parent_list = unique_ordered_list(self.test_picturae_importer_lite.parent_list)

            for index, taxon in reversed(list(enumerate(self.test_picturae_importer_lite.taxon_list))):

                author_insert, tree_item_id, \
                rank_end, parent_id, taxon_guid, rank_id = self.test_picturae_importer_lite.generate_taxon_fields(
                                                           index=index, taxon=taxon)

                test_parent_id = self.sql_csv_tools.get_one_match(id_col="TaxonID", tab_name="taxon",
                                                                  key_col="FullName",
                                                                  match=self.test_picturae_importer_lite.parent_list[index+1],
                                                                  match_type="string")


                self.assertEqual(parent_id, test_parent_id)

                if self.test_picturae_importer_lite.is_hybrid is False and taxon == self.test_picturae_importer_lite.full_name:
                    self.assertEqual(author_insert, row['accepted_author'])

                elif self.test_picturae_importer_lite.is_hybrid is False:
                    pass

                elif self.test_picturae_importer_lite.is_hybrid is True:
                    self.assertTrue(pd.isna(author_insert))

                self.assertEqual(rank_id, rank_list[rank_num])

                self.assertEqual(rank_end, tax_ends[rank_num])

                rank_num += 1



    def test_taxon_insert(self):
        """test_taxon_insert: tests the insert function which inserts taxon fields into
                              database, makes sure column assignments return correctly
        """

        for index, row in self.test_picturae_importer_lite.record_full.iterrows():
            self.test_picturae_importer_lite.populate_fields(row)
            # self.test_picturae_importer_lite.taxon_guid = uuid4()
            self.test_picturae_importer_lite.taxon_list = []

            self.test_picturae_importer_lite.populate_taxon()


            self.test_picturae_importer_lite.taxon_guid = uuid4()

            self.test_picturae_importer_lite.parent_list = [self.test_picturae_importer_lite.full_name,
                                                            self.test_picturae_importer_lite.first_intra,
                                                            self.test_picturae_importer_lite.gen_spec,
                                                            self.test_picturae_importer_lite.genus,
                                                            self.test_picturae_importer_lite.family_name]

            self.test_picturae_importer_lite.parent_list = unique_ordered_list(self.test_picturae_importer_lite.parent_list)

            self.test_picturae_importer_lite.create_taxon()
            for index, taxon in reversed(list(enumerate(self.test_picturae_importer_lite.taxon_list))):


                author_insert, tree_item_id, \
                rank_end, parent_id, taxon_guid, rank_id = self.test_picturae_importer_lite.generate_taxon_fields(
                                                           index=index, taxon=taxon)

                column_list = ['TimestampCreated',
                               'TimestampModified',
                               'Version',
                               'Author',
                               'FullName',
                               'GUID',
                               'Source',
                               'IsAccepted',
                               'IsHybrid',
                               'Name',
                               'RankID',
                               'TaxonTreeDefID',
                               'ParentID',
                               'ModifiedByAgentID',
                               'CreatedByAgentID',
                               'TaxonTreeDefItemID']

                value_list = [f"{time_utils.get_pst_time_now_string()}",
                              f"{time_utils.get_pst_time_now_string()}",
                              1,
                              author_insert,
                              f"{taxon}",
                              f"{taxon_guid}",
                              "World Checklist of Vascular Plants 2023",
                              True,
                              self.test_picturae_importer_lite.is_hybrid,
                              f"{rank_end}",
                              f"{rank_id}",
                              1,
                              f"{parent_id}",
                              f"{self.test_picturae_importer_lite.created_by_agent}",
                              f"{self.test_picturae_importer_lite.created_by_agent}",
                              f"{tree_item_id}"
                              ]

                value_list, column_list = remove_two_index(value_list, column_list)

                sql = self.sql_csv_tools.create_insert_statement(tab_name="taxon",
                                                                 col_list=column_list,
                                                                 val_list=value_list)
                self.sql_csv_tools.insert_table_record(logger_int=self.logger, sql=sql)


                # pulling sample taxon to make sure columns line up


                # checking taxname
                pull_name_end = self.sql_csv_tools.get_one_match(id_col="Name", tab_name="taxon",
                                                                 key_col="FullName",
                                                                 match=taxon,
                                                                 match_type="string")

                self.assertEqual(pull_name_end, rank_end)

                # checking parent id

                pull_parent = self.sql_csv_tools.get_one_match(id_col="ParentID", tab_name="taxon",
                                                               key_col="FullName",
                                                               match=taxon,
                                                               match_type="string")

                self.assertEqual(pull_parent, parent_id)


                # checking taxon id
                pull_taxid = self.sql_csv_tools.get_one_match(id_col="TaxonID", tab_name="taxon",
                                                              key_col="FullName",
                                                              match=taxon,
                                                              match_type="string")

                self.assertFalse(pd.isna(pull_taxid))

                logging.info(f"test taxon: {taxon} created")


    def tearDown(self):
        del self.test_picturae_importer_lite
        # restoring db to original state removing backup
        shutil.copyfile("../tests/casbotany_backup.db", "../tests/casbotany_lite.db")
        os.remove("../tests/casbotany_backup.db")



if __name__ == '__main__':
    unittest.main()