"""this takes the csv data from picturae_csv_create, and parses the fields on a row by row basis into new db records,
    filling in the necessary relational tables, and uploading attached images to image server.
    Used as part of picturae_project for upload post-imaging, to create records to be updated post OCR and transcription
"""
import atexit
import traceback
import picturae_config
from rpy2 import robjects
from rpy2.robjects import pandas2ri
from uuid import uuid4
from data_utils import *
import logging
from sql_csv_utils import *
from importer import Importer
from picturae_csv_create import CsvCreatePicturae
from sql_csv_utils import generate_token
from botany_importer import BotanyImporter

from picturae_csv_create import starting_time_stamp

class PicturaeImporter(Importer):
    """DataOnboard:
           A class with methods designed to wrangle, verify,
           and upload a csv file containing transcribed
           specimen sheet records into the casbotany database,
           along with attached images
    """

    def __init__(self, paths, date_string=None):
        super().__init__(picturae_config, "Botany")

        if date_string is None:
            self.date_use = get_max_subdirectory_date("picturae_csv")
        else:
            self.date_use = date_string

        self.logger = logging.getLogger('PicturaeImporter')
        # full collector list is for populating existing and missing agents into collector table
        # new_collector_list is only for adding new agents to agent table.
        empty_lists = ['barcode_list', 'image_list', 'full_collector_list', 'new_collector_list',
                       'taxon_list']

        for empty_list in empty_lists:
            setattr(self, empty_list, [])

        self.no_match_dict = {}

        # running csv create
        CsvCreatePicturae(date_string=self.date_use)

        self.file_path = f"PIC_upload/PIC_record_{self.date_use}.csv"

        self.record_full = pd.read_csv(self.file_path)

        self.batch_size = len(self.record_full)

        # intializing parameters for database upload
        init_list = ['GeographyID', 'taxon_id', 'barcode',
                     'verbatim_date', 'start_date', 'end_date',
                     'collector_number', 'locality', 'collecting_event_guid',
                     'collecting_event_id', 'locality_guid', 'agent_guid',
                     'geography_string', 'GeographyID', 'locality_id',
                     'full_name', 'tax_name', 'locality',
                     'determination_guid', 'collection_ob_id', 'collection_ob_guid',
                     'name_id', 'author_sci', 'family', 'gen_spec_id', 'family_id', 'parent_author']

        for param in init_list:
            setattr(self, param, None)

        self.created_by_agent = 99726

        self.batch_md5 = generate_token(starting_time_stamp, self.file_path)

        self.paths = paths

        self.run_all_methods()


    def run_timestamps(self, batch_size: int):
        """updating md5 fields for new taxon and taxon mismatch batches"""
        ending_time_stamp = datetime.now()

        sql = create_timestamps(start_time=starting_time_stamp, end_time=ending_time_stamp,
                                batch_md5=self.batch_md5, batch_size=batch_size)

        self.create_table_record(sql)

        condition = f'''WHERE TimestampCreated >= "{starting_time_stamp}" 
                        AND TimestampCreated <= "{ending_time_stamp}";'''

        error_tabs = ['taxa_unmatch', 'picturaetaxa_added']
        for tab in error_tabs:

            sql = create_update_statement(tab_name=tab, col_list=['batch_MD5'], val_list=[self.batch_md5],
                                       condition=condition)
            self.create_table_record(sql)


    def time_stamper(self):
        """time_stamper: runs timestamp at beginning of script and at exit,
                        uses the create_timestamps function from data_utils
                        to append timestamps with codes to csvs,
                        for record purging"""
        # marking starting time stamp
        # at exit run ending timestamp and append timestamp csv
        atexit.register(self.run_timestamps, batch_size=self.batch_size)

    def unlock_account(self):
        """function to be called during unexpected interruption of upload,
           so DB doesn't accidently remain locked"""

        sql = """ALTER USER 'botanist'@'%' ACCOUNT UNLOCK;"""

        self.create_table_record(sql)

    def col_dtypes(self):
        """just in case csv import changes column dtypes, resetting at top of file,
            re-standardizing null and nan records to all be pd.NA() and
            evaluate strings into booleans
        """
        # setting datatypes for columns
        string_list = self.record_full.columns.to_list()

        self.record_full[string_list] = self.record_full[string_list].astype(str)

        self.record_full = self.record_full.replace({'True': True, 'False': False})

        self.record_full = self.record_full.replace(['', None, 'nan', np.nan], pd.NA)

    def taxon_assign_defitem(self, taxon_string):
        """taxon_assign_defitme: assigns, taxon rank and treeitemid number,
                                based on subtrings present in taxon name.
            args:
                taxon_string: the taxon string or substring, which before assignment
        """
        def_tree = 13
        rank_id = 220
        if "subsp." in taxon_string:
            def_tree = 14
            rank_id = 230
        if "var." in taxon_string:
            def_tree = 15
            rank_id = 240
        if "subvar." in taxon_string:
            def_tree = 16
            rank_id = 250
        if " f. " in taxon_string:
            def_tree = 17
            rank_id = 260
        if "subf." in taxon_string:
            def_tree = 21
            rank_id = 270
        if len(taxon_string.split()) == 1:
            def_tree = 12
            rank_id = 180

        return def_tree, rank_id

    def check_single_taxa(self, taxon_name, barcode):
        """check_single_taxa: designed to take in one taxaname and
           do a TNRS operation on it to get an author for iterative higher taxa.

           args:
                taxon_name: a string of a taxon name, or a parsed genus or family, used to control
                            for unconfirmed species, and spelling mistakes.
                barcode: the string barcode of the taxon name associated with each photo.
                         used to re-merge dataframes after TNRS and keep track of the record in R.
        """
        taxon_frame = {"CatalogNumber": [barcode], "fullname": [taxon_name]}

        taxon_frame = pd.DataFrame(taxon_frame)

        pandas2ri.activate()

        r_dataframe_tax = pandas2ri.py2rpy(taxon_frame)

        robjects.globalenv['r_dataframe_taxon'] = r_dataframe_tax

        with open('taxon_check/R_TNRS.R', 'r') as file:
            r_script = file.read()

        robjects.r(r_script)

        resolved_taxon = robjects.r['resolved_taxa']

        resolved_taxon = robjects.conversion.rpy2py(resolved_taxon)

        taxon_list = list(resolved_taxon['accepted_author'])

        self.parent_author = taxon_list[0]

    # think of finding way to make this function logic not so repetitive
    def create_file_list(self):
        """create_file_list: creates a list of imagepaths and barcodes for upload,
                                after checking conditions established to prevent
                                overwriting data functions
        """
        for index, row in self.record_full.iterrows():
            if not row['image_valid']:
                raise ValueError(f"image {row['image_path']} is not valid ")

            elif not row['is_barcode_match']:
                raise ValueError(f"image barcode {row['image_path']} does not match "
                                 f"{row['CatalogNumber']}")

            elif row['barcode_present'] and row['image_present']:
                self.logger.warning(f"record {row['CatalogNumber']} and image {row['image_path']}"
                                    f" already in database")

            elif row['barcode_present'] and not row['image_present']:
                self.logger.warning(f"record {row['CatalogNumber']} "
                                    f"already in database, appending image")
                self.image_list.append(row['image_path'])

            elif not row['barcode_present'] and row['image_present']:
                self.logger.warning(f"image {row['image_path']} "
                                    f"already in database, appending record")
                self.barcode_list.append(row['CatalogNumber'])
            # create case so that if two duplicate rows , but with different images, upload both images,
            # but not both rows
            else:
                self.image_list.append(row['image_path'])
                self.barcode_list.append(row['CatalogNumber'])
                self.barcode_list = list(set(self.barcode_list))
                self.image_list = list(set(self.image_list))
    def create_agent_list(self, row):
        """create_agent_list:
                creates a list of collectors that will be checked and added to agent/collector tables.
                checks each collector first and last name against the database, and
                then if absent, appends the new agent name to a list of dictionaries self.collector_list.
           args:
                row: a dataframe row containing collector name information
        """
        self.new_collector_list = []
        self.full_collector_list = []

        column_names = list(self.record_full.columns)
        for i in range(1, 6):
            try:
                first_index = column_names.index(f'collector_first_name{i}')
                middle_index = column_names.index(f'collector_middle_name{i}')
                last_index = column_names.index(f'collector_last_name{i}')

                first = row[first_index]
                middle = row[middle_index]
                last = row[last_index]

            except ValueError:
                break
            # need a way to keep ones with nas, but only split titles from real names
            if not pd.isna(first) or not pd.isna(middle) or not pd.isna(last):
                # first name title taking priority over last
                first_name, title = assign_titles(first_last='first', name=f"{first}")
                last_name, title = assign_titles(first_last='last', name=f"{last}")

                middle = middle
                elements = [first_name, last_name, title, middle]

                for index in range(len(elements)):
                    if elements[index] == '':
                        elements[index] = pd.NA

                first_name, last_name, title, middle = elements

                sql = check_agent_name_sql(first_name, last_name, middle, title)

                agent_id = self.specify_db_connection.get_one_record(sql)

                collector_dict = {f'collector_first_name': first_name,
                                  f'collector_middle_initial': middle,
                                  f'collector_last_name': last_name,
                                  f'collector_title': title}

                self.full_collector_list.append(collector_dict)
                if agent_id is None:
                    self.new_collector_list.append(collector_dict)

    # check after getting real dataset, still not final

    def populate_sql(self, tab_name, id_col, key_col, match, match_type="string"):
        """populate_sql:
                creates a custom select statement for get one record,
                from which a result can be gotten more seamlessly
                without having to rewrite the sql variable every time
           args:
                tab_name: the name of the table to select
                id_col: the name of the column in which the unique id is stored
                key_col: column on which to match values
                match: value with which to match key_col
        """
        sql = ""
        if match_type == "string":
            sql = f'''SELECT {id_col} FROM {tab_name} WHERE `{key_col}` = "{match}";'''
        elif match_type == "integer":
            sql = f'''SELECT {id_col} FROM {tab_name} WHERE `{key_col}` = {match};'''

        result = self.specify_db_connection.get_one_record(sql)

        return result

    def populate_fields(self, row):
        """populate_fields:
               this populates all the
               initialized data fields per row for input into database,
               make sure to check column list is correct so that the
               row indexes are assigned correctly.
           args:
                row: a row from a botany specimen csv dataframe containing the required columns

        """
        column_list = ['CatalogNumber', 'verbatim_date', 'start_date',
                       'end_date', 'collector_number', 'locality', 'fullname', 'taxname',
                       'gen_spec', 'qualifier', 'name_matched', 'Genus', 'Family', 'Hybrid', 'accepted_author',
                       'name_matched', 'first_intra', 'county', 'state', 'country']
        # print(self.full_name)
        index_list = []
        for column in column_list:
            barcode_index = self.record_full.columns.get_loc(column)
            index_list.append(barcode_index)
        self.barcode = row[index_list[0]].zfill(9)
        self.verbatim_date = row[index_list[1]]
        self.start_date = row[index_list[2]]
        self.end_date = row[index_list[3]]
        self.collector_number = row[index_list[4]]
        self.locality = row[index_list[5]]
        self.full_name = row[index_list[6]]
        self.tax_name = row[index_list[7]]
        self.gen_spec = row[index_list[8]]
        self.qualifier = row[index_list[9]]
        self.name_matched = row[index_list[10]]
        self.genus = row[index_list[11]]
        self.family_name = row[index_list[12]]
        self.is_hybrid = row[index_list[13]]
        self.author = row[index_list[14]]
        self.name_matched = row[index_list[15]]
        self.first_intra = row[index_list[16]]

        guid_list = ['collecting_event_guid', 'collection_ob_guid', 'locality_guid', 'determination_guid']
        for guid_string in guid_list:
            setattr(self, guid_string, uuid4())

        self.geography_string = str(row[index_list[17]]) + ", " + \
                                str(row[index_list[18]]) + ", " + str(row[index_list[19]])

        self.GeographyID = self.populate_sql(tab_name='geography', id_col='GeographyID',
                                             key_col='FullName', match=self.geography_string)

        self.locality_id = self.populate_sql(tab_name='locality', id_col='LocalityID',
                                             key_col='LocalityName', match=self.locality)

    def taxon_get(self, name):
        sql = f'''SELECT TaxonID FROM casbotany.taxon WHERE FullName = "{name}";'''
        result_id = self.specify_db_connection.get_one_record(sql)
        return result_id

    # this process will be simplified to reflect new (8/31) changes in picturae_csv_create.py
    def populate_taxon(self):
        """populate taxon: creates a taxon list, which checks different rank levels in the taxon,
                         as genus must be uploaded before species , before sub-taxa etc...
                         has cases for hybrid plants, uses regex to separate out sub-taxa hybrids,
                          uses parsed lengths to separate out genus level and species level hybrids.
                        cf. qualifiers already seperated, so less risk of confounding notations.
        """
        self.gen_spec_id = None
        self.taxon_list = []
        self.taxon_id = self.taxon_get(name=self.full_name)
        # append taxon full name
        if self.taxon_id is None:
            self.taxon_list.append(self.full_name)
            # check base name if base name differs e.g. if var. or subsp.
            if self.full_name != self.first_intra and self.first_intra != self.gen_spec:
                self.first_intra_id = self.taxon_get(name=self.first_intra)
                if self.first_intra_id is None:
                    self.taxon_list.append(self.gen_spec)

            if self.full_name != self.gen_spec:
                self.gen_spec_id = self.taxon_get(name=self.gen_spec)
                self.check_single_taxa(taxon_name=self.gen_spec, barcode=self.barcode)
                # adding base name to taxon_list
                if self.gen_spec_id is None:
                    self.taxon_list.append(self.gen_spec)

            # base value for gen spec is set as None so will work either way.
            # checking for genus id
                self.genus_id = self.taxon_get(name=self.genus)
                # adding genus name if missing
                if self.genus_id is None:
                    self.taxon_list.append(self.genus)

                    # checking family id
                    # self.family_id = self.taxon_get(name=self.family_name)
                    # # adding family name to list
                    # if self.family_id is None:
                    #     self.taxon_list.append(self.family_name)
        else:
            pass


    def create_table_record(self, sql):
        """create_table_record:
               general code for the inserting of a new record into any table on casbotany.
               creates connection, and runs sql query. cursor.execute with arg multi, to
               handle multi-query commands.
           args:
               sql: the verbatim sql string, or multi sql query string to send to database
               is_test: set to False as default, if switched to true,
                        uses sql-lite database instead for testing.
        """
        cursor = self.specify_db_connection.get_cursor()

        self.logger.info(f'running query: {sql}')
        self.logger.debug(sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f"Exception thrown while processing sql: {sql}\n{e}\n", flush=True)
            self.logger.error(traceback.format_exc())
        try:
            self.specify_db_connection.commit()

        except Exception as e:
            self.logger.error(f"sql debug: {e}")
            sys.exit("terminating script")

        cursor.close()



    def create_locality_record(self):
        """create_locality_record:
               defines column and value list , runs them as args
               through create_sql_string and create_table record
               in order to add new locality record to database
        """

        table = 'locality'

        column_list = ['TimestampCreated',
                       'TimestampModified',
                       'Version',
                       'GUID',
                       'SrcLatLongUnit',
                       'OriginalLatLongUnit',
                       'LocalityName',
                       'DisciplineID',
                       'GeographyID',
                       'ModifiedByAgentID',
                       'CreatedByAgentID'
                       ]

        value_list = [f'{time_utils.get_pst_time_now_string()}',
                      f'{time_utils.get_pst_time_now_string()}',
                      1,
                      f"{self.locality_guid}",
                      0,
                      0,
                      f"{self.locality}",
                      3,
                      f"{self.GeographyID}",
                      f'{self.created_by_agent}',
                      f'{self.created_by_agent}']

        # removing na values from both lists
        value_list, column_list = remove_two_index(value_list, column_list)

        sql = create_insert_statement(tab_name=table, col_list=column_list,
                                val_list=value_list)

        self.create_table_record(sql=sql)

    def create_agent_id(self):
        """create_agent_id:
                defines column and value list , runs them as
                args through create_sql_string and create_table record
                in order to add new agent record to database.
                Includes a forloop to cycle through multiple collectors.
         """
        table = 'agent'
        for name_dict in self.new_collector_list:
            self.agent_guid = uuid4()

            columns = ['TimestampCreated',
                       'TimestampModified',
                       'Version',
                       'AgentType',
                       'DateOfBirthPrecision',
                       'DateOfDeathPrecision',
                       'FirstName',
                       'LastName',
                       'MiddleInitial',
                       'Title',
                       'DivisionID',
                       'GUID',
                       'ModifiedByAgentID',
                       'CreatedByAgentID']

            values = [f'{time_utils.get_pst_time_now_string()}',
                      f'{time_utils.get_pst_time_now_string()}',
                      1,
                      1,
                      1,
                      1,
                      f"{name_dict['collector_first_name']}",
                      f"{name_dict['collector_last_name']}",
                      f"{name_dict['collector_middle_initial']}",
                      f"{name_dict['collector_title']}",
                      2,
                      f'{self.agent_guid}',
                      f'{self.created_by_agent}',
                      f'{self.created_by_agent}'
                      ]
            # removing na values from both lists
            values, columns = remove_two_index(values, columns)

            sql = create_insert_statement(tab_name=table, col_list=columns,
                                    val_list=values)

            self.create_table_record(sql=sql)

    def create_collecting_event(self):
        """create_collectingevent:
                defines column and value list , runs them as
                args through create_sql_string and create_table record
                in order to add new collectingevent record to database.
         """

        # re-pulling locality id to reflect update

        self.locality_id = self.populate_sql(tab_name='locality', id_col='LocalityID',
                                             key_col='LocalityName', match=self.locality)

        table = 'collectingevent'

        column_list = ['TimestampCreated',
                       'TimestampModified',
                       'Version',
                       'GUID',
                       'DisciplineID',
                       'StationFieldNumber',
                       'VerbatimDate',
                       'StartDate',
                       'EndDate',
                       'LocalityID',
                       'ModifiedByAgentID',
                       'CreatedByAgentID'
                       ]

        value_list = [f'{time_utils.get_pst_time_now_string()}',
                      f'{time_utils.get_pst_time_now_string()}',
                      0,
                      f'{self.collecting_event_guid}',
                      3,
                      f'{self.collector_number}',
                      f'{self.verbatim_date}',
                      f'{self.start_date}',
                      f'{self.end_date}',
                      f'{self.locality_id}',
                      f'{self.created_by_agent}',
                      f'{self.created_by_agent}'
                      ]

        # removing na values from both lists
        value_list, column_list = remove_two_index(value_list, column_list)

        sql = create_insert_statement(tab_name=table, col_list=column_list,
                                val_list=value_list)

        self.create_table_record(sql=sql)

    # temporarily creating exception list until reliable taxon protocol
    def create_taxon(self):
        """create_taxon: populates the taxon table iteratively by adding higher taxa first,
                            before lower taxa. Assigns taxa ranks and TaxonTreedefItemID
        """
        # for now do not upload
        parent_list = [self.full_name, self.first_intra, self.gen_spec, self.genus, self.family_name]
        parent_list = unique_ordered_list(parent_list)
        for index, taxa_rank in reversed(list(enumerate(self.taxon_list))):
            taxon_guid = uuid4()
            rank_name = taxa_rank
            parent_id = self.taxon_get(name=parent_list[index + 1])
            table = 'taxon'
            if taxa_rank == self.full_name:
                rank_end = self.tax_name
            else:
                rank_end = taxa_rank.split()[-1]

            author_insert = self.author

            if rank_name != self.family_name:
                tree_item_id, rank_id = self.taxon_assign_defitem(taxon_string=rank_name)
            else:
                rank_id = 140
                tree_item_id = 11

            if rank_id < 220:
                author_insert = pd.NA

            # assigning parent_author if needed , for gen_spec

            if rank_id == 220 and self.full_name != self.gen_spec:
                author_insert = self.parent_author

            if self.is_hybrid is True:
                author_insert = pd.NA


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
                          f"{rank_name}",
                          f"{taxon_guid}",
                          "World Checklist of Vascular Plants 2023",
                          True,
                          self.is_hybrid,
                          f"{rank_end}",
                          f"{rank_id}",
                          1,
                          f"{parent_id}",
                          f"{self.created_by_agent}",
                          f"{self.created_by_agent}",
                          f"{tree_item_id}"
                          ]

            value_list, column_list = remove_two_index(value_list, column_list)

            sql = create_insert_statement(tab_name=table, col_list=column_list,
                                    val_list=value_list)

            self.create_table_record(sql=sql)

            print("taxon_created!")

    def create_collection_object(self):
        """create_collection_object:
                defines column and value list , runs them as
                args through create_sql_string and create_table record
                in order to add new collectionobject record to database.
        """
        # will new collecting event ids need to be created ?
        # re-pulling collecting event id to reflect new record

        self.collecting_event_id = self.populate_sql(tab_name='collectingevent', id_col='CollectingEventID',
                                                     key_col='GUID', match=self.collecting_event_guid)

        table = 'collectionobject'

        column_list = ['TimestampCreated',
                       'TimestampModified',
                       'CollectingEventID',
                       'Version',
                       'CollectionMemberID',
                       'CatalogNumber',
                       'CatalogedDate',
                       'CatalogedDatePrecision',
                       'GUID',
                       'CollectionID',
                       'Date1Precision',
                       'InventoryDatePrecision',
                       'ModifiedByAgentID',
                       'CreatedByAgentID',
                       'CatalogerID'
                       ]

        value_list = [f"{time_utils.get_pst_time_now_string()}",
                      f"{time_utils.get_pst_time_now_string()}",
                      f"{self.collecting_event_id}",
                      0,
                      4,
                      f"{self.barcode}",
                      f"{starting_time_stamp.strftime('%Y-%m-%d')}",
                      1,
                      f"{self.collection_ob_guid}",
                      4,
                      1,
                      1,
                      f"{self.created_by_agent}",
                      f"{self.created_by_agent}",
                      f"{self.created_by_agent}"]

        # removing na values from both lists
        value_list, column_list = remove_two_index(value_list, column_list)

        sql = create_insert_statement(tab_name=table, col_list=column_list,
                                val_list=value_list)

        self.create_table_record(sql=sql)

    def create_determination(self):
        """create_determination:
                inserts data into determination table, and ties it to collection object table.
           args:
                none
           returns:
                none
        """
        table = 'determination'

        self.collection_ob_id = self.populate_sql(tab_name='collectionobject', id_col='CollectionObjectID',
                                                  key_col='GUID', match=self.collection_ob_guid)

        self.taxon_id = self.populate_sql(tab_name='taxon', id_col='TaxonID',
                                          key_col='FullName', match=self.full_name)
        if self.taxon_id is not None:

            column_list = ['TimestampCreated',
                           'TimestampModified',
                           'Version',
                           'CollectionMemberID',
                           # 'DeterminedDate',
                           'DeterminedDatePrecision',
                           'IsCurrent',
                           'Qualifier',
                           'GUID',
                           'TaxonID',
                           'CollectionObjectID',
                           'ModifiedByAgentID',
                           'CreatedByAgentID',
                           # 'DeterminerID',
                           'PreferredTaxonID',
                           ]
            value_list = [f"{time_utils.get_pst_time_now_string()}",
                          f"{time_utils.get_pst_time_now_string()}",
                          1,
                          4,
                          1,
                          True,
                          f"{self.qualifier}",
                          f"{self.determination_guid}",
                          f"{self.taxon_id}",
                          f"{self.collection_ob_id}",
                          f"{self.created_by_agent}",
                          f"{self.created_by_agent}",
                          f"{self.taxon_id}",
                          ]

            # removing na values from both lists
            value_list, column_list = remove_two_index(value_list, column_list)

            sql = create_insert_statement(tab_name=table, col_list=column_list,
                                    val_list=value_list)
            self.create_table_record(sql)

        else:
            self.logger.error(f"failed to add determination , missing taxon for {self.full_name}")
            sys.exit()

    def create_collector(self):
        """create_collector:
                adds collector to collector table, after pulling collection object, agent codes.
           args:
                none
           returns:
                none
        """
        primary_bool = [True, False, False, False, False]
        for index, agent_dict in enumerate(self.full_collector_list):
            table = 'collector'

            sql = check_agent_name_sql(first_name=agent_dict["collector_first_name"],
                                        last_name=agent_dict["collector_last_name"],
                                        middle_initial=agent_dict["collector_middle_initial"],
                                        title=agent_dict["collector_title"])

            agent_id = self.specify_db_connection.get_one_record(sql=sql)

            column_list = ['TimestampCreated',
                           'TimestampModified',
                           'Version',
                           'IsPrimary',
                           'OrderNumber',
                           'ModifiedByAgentID',
                           'CreatedByAgentID',
                           'CollectingEventID',
                           'DivisionID',
                           'AgentID']

            value_list = [f"{time_utils.get_pst_time_now_string()}",
                          f"{time_utils.get_pst_time_now_string()}",
                          1,
                          primary_bool[index],
                          1,
                          f"{self.created_by_agent}",
                          f"{self.created_by_agent}",
                          f"{self.collecting_event_id}",
                          2,
                          f"{agent_id}"]

            # removing na values from both lists
            value_list, column_list = remove_two_index(value_list, column_list)

            sql = create_insert_statement(tab_name=table, col_list=column_list,
                                    val_list=value_list)

            self.create_table_record(sql)

    def hide_unwanted_files(self):
        """hide_unwanted_files:
               function to hide files inside of images folder,
               to filter out images not in images_list. Adds a substring '.hidden_'
               in front of base file name.
           args:
                none
           returns:
                none
        """
        sla = os.path.sep
        folder_path = f'picturae_img/PIC_{self.date_use}{sla}'
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if file_path not in self.image_list:
                new_file_name = f".hidden_{file_name}"
                new_file_path = os.path.join(folder_path, new_file_name)
                os.rename(file_path, new_file_path)

    def unhide_files(self):
        """unhide_files:
                will directly undo the result of hide_unwanted_files.
                Removes substring `.hidden_` from all base filenames
           args:
                none
           returns:
                none
        """
        sla = os.path.sep
        folder_path = f'picturae_img/PIC_{self.date_use}{sla}'
        prefix = ".hidden_"  # The prefix added during hiding
        for file_name in os.listdir(folder_path):
            if file_name.startswith(prefix):
                old_file_name = file_name[len(prefix):]
                old_file_path = os.path.join(folder_path, old_file_name)
                new_file_path = os.path.join(folder_path, file_name)
                os.rename(new_file_path, old_file_path)

    def upload_records(self):
        """upload_records:
               an ensemble function made up of all row level, and database functions,
               loops through each row of the csv, updates the global values, and creates new table records
           args:
                none
            returns:
                new table records related
        """
        # the order of operations matters, if you change the order certain variables may overwrite


        self.record_full = self.record_full[self.record_full['CatalogNumber'].isin(self.barcode_list)]

        self.record_full = self.record_full.drop_duplicates(subset=['CatalogNumber'])


        for index, row in self.record_full.iterrows():
            self.populate_fields(row)
            self.create_agent_list(row)
            self.populate_taxon()
            if self.taxon_id is None:
                self.create_taxon()

            if self.locality_id is None:
                self.create_locality_record()

            if len(self.new_collector_list) > 0:
                self.create_agent_id()

            self.create_collecting_event()

            self.create_collection_object()

            self.create_determination()

            self.create_collector()


    def upload_attachments(self):
        """upload_attachments:
                this function runs Botany importer
                Updates date in
                picturae_config to ensure prefix is
                updated for correct filepath
        """
        filename = "picturae_config.py"

        latest_date = r'\1"' + self.date_use + r'"\n'


        with open(filename, 'r') as file:
            # Read the contents of the file
            content = file.read()

        # Replace the string
        new_content = re.sub(r'(date_str = )(.*?)\n', latest_date, content)

        with open(filename, 'w') as file:
            # Write the modified content back to the file
            file.write(new_content)

        try:
            self.hide_unwanted_files()

            BotanyImporter(paths=self.paths, config=picturae_config)

            self.unhide_files()
        except Exception as e:
            self.logger.error(f"{e}")

    def run_all_methods(self):
        """run_all_methods:
                        self-explanatory function, will run all function in class in sequential manner"""

        # create_test_images(list(range(999999981, 999999985)), date_string=self.date_use)

        # setting directory
        to_current_directory()

        self.col_dtypes()

        # creating file list after conditions
        self.create_file_list()

        # prompt
        cont_prompter()

        # locking users out from the database

        sql = """UPDATE mysql.user
                 SET account_locked = 'Y'
                 WHERE user != 'botanist' AND host = '%';"""

        self.create_table_record(sql)

        # starting purge timer
        self.time_stamper()

        # creating tables

        self.upload_records()

        # creating new taxon list
        if len(self.taxon_list) > 0:
            taxa_frame = self.record_full[self.record_full['fullname'].isin(self.taxon_list)]
            for index, row in taxa_frame.iterrows():
                catalog_number = taxa_frame.columns.get_loc('CatalogNumber')
                barcode_result = self.populate_sql(tab_name='picturaetaxa_added',
                                        id_col='CatalogNumber',
                                        key_col='CatalogNumber',
                                        match=row[catalog_number],
                                        match_type="integer"
                                        )
                if barcode_result is None:
                    sql = create_new_tax_tab(row=row, df=taxa_frame, tab_name='picturaetaxa_added')
                    self.create_table_record(sql)

        # uploading attachments
        self.upload_attachments()

        # writing time stamps to txt file

        self.logger.info("process finished")

        # unlocking database

        sql = """UPDATE mysql.user
                 SET account_locked = 'n'
                 WHERE user != 'botanist' AND host = '%';"""

        self.create_table_record(sql)
