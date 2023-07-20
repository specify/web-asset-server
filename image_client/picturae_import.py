"""this file will be used to parse the data from Picturae into an uploadable format to Specify"""
import picturae_config
import sys
import os
import time_utils
from uuid import uuid4
from data_utils import *
from importer import Importer
import subprocess
import pandas as pd
from casbotany_sql_lite import *
import client_tools
from datetime import date
import math
from PIL import Image
import traceback
import logging


class DataOnboard(Importer):
    """DataOnboard:
           A class with methods designed to wrangle, verify, and upload a csv file
           containing transcribed specimen sheet records into the casbotany database, along with attached,
           images
    """
    def __init__(self, date_string):
        super().__init__(picturae_config, "Botany")
        self.date_use = date_string
        self.logger = logging.getLogger('DataOnboard')
        self.barcode_list = []
        self.image_list = []
        self.collector_list = []
        self.agent_guid_list = []
        self.sql_concat = ""
        self.record_full = pd.DataFrame()
        # intializing parameters for database upload
        init_list = ['barcode', 'verbatim_date', 'start_date', 'end_date',
                     'collector_number', 'locality', 'collecting_event_guid',
                     'locality_guid', 'agent_guid', 'geography_string',
                     'GeographyID', 'locality_id', 'full_name', 'tax_name',
                     'locality']
        for param in init_list:
            setattr(self, param, None)

        self.created_by_agent = 99726

    def to_current_directory(self):
        """to_current_directory: changes current directory to .py file location
            args:
                none
            returns:
                resets current directory to source file location
        """
        current_file_path = os.path.abspath(__file__)

        directory = os.path.dirname(current_file_path)

        os.chdir(directory)

    def file_present(self):
        """file_present:
           checks if correct filepath in working directory,
           checks if file is on input date
           checks if file folder is present.
           uses self.use_date to decide which folders to check
           args:
                none
        """

        self.to_current_directory()

        dir_sub = os.path.isdir(str("picturae_csv/") + str(self.date_use))

        if dir_sub is True:
            folder_path = 'picturae_csv/' + str(self.date_use) + '/picturae_folder(' + \
                           str(self.date_use) + ').csv'

            specimen_path = 'picturae_csv/' + str(self.date_use) + '/picturae_specimen(' + \
                             str(self.date_use) + ').csv'

            if os.path.exists(folder_path):
                print("Folder csv exists!")
            else:
                raise ValueError("Folder csv does not exist")

            if os.path.exists(specimen_path):
                print("Specimen csv exists!")
            else:
                raise ValueError("Specimen csv does not exist")
        else:
            raise ValueError(f"subdirectory for {self.date_use} not present")

    def csv_read_folder(self, folder_string):
        """csv_read_folder:
                reads in csv data for given date self.date_use
        args:
            folder_string: denotes whether specimen or folder level data with "folder" or "specimen"
        """

        folder_path = 'picturae_csv/' + str(self.date_use) + '/picturae_' + str(folder_string) + '(' + \
                       str(self.date_use) + ').csv'

        folder_csv = pd.read_csv(folder_path)

        return folder_csv

    def csv_merge(self):
        """csv_merge: merges the folder_csv and the specimen_csv on barcode
       args:
            fold_csv: folder level csv to be input as argument for merging
            spec_csv: specimen level csv to be input as argument for merging """
        fold_csv = self.csv_read_folder("folder")
        spec_csv = self.csv_read_folder("specimen")

        # checking if columns to merge contain same data
        if (set(fold_csv['specimen_barcode']) == set(spec_csv['specimen_barcode'])) is True:
            # removing duplicate columns
            # (Warning! will want to double-check whether these columns are truly the
            # same between datasets when more info received)

            common_columns = list(set(fold_csv.columns).intersection(set(spec_csv.columns)))

            common_columns.remove('specimen_barcode')

            spec_csv = spec_csv.drop(common_columns, axis=1)

            # completing merge on barcode
            self.record_full = pd.merge(fold_csv, spec_csv,
                                        on='specimen_barcode', how='inner')

        else:
            raise ValueError("Barcode Columns do not match!")

    def csv_colnames(self):
        """csv_colnames: function to be used to rename columns to specify standards"""
        # remove columns !! review when real dataset received

        col_names = self.record_full.columns

        cols_drop = ['application_batch', 'csv_batch', 'object_type', 'filed_as_family',
                     'barcode_info', 'Notes', 'Feedback']
        # dropping empty columns
        self.record_full = self.record_full.drop(columns=cols_drop)

        # self.record_full = self.record_full.dropna(axis=1, how='all')

        # some of these are just placeholders for now

        col_dict = {'Country': 'country',
                    'State': 'state',
                    'County': 'county',
                    'specimen_barcode': 'CatalogNumber',
                    'path_jpg': 'image_path',
                    'collector_number': 'collector_number',
                    'collector_first_name 1': 'collector_first_name1',
                    'collector_middle_name 1': 'collector_middle_name1',
                    'collector_last_name 1': 'collector_last_name1',
                    'collector_first_name 2': 'collector_first_name2',
                    'collector_middle_name 2': 'collector_middle_name2',
                    'collector_last_name 2': 'collector_last_name2',
                    'collector_first_name 3': 'collector_first_name3',
                    'collector_middle_name 3': 'collector_middle_name3',
                    'collector_last_name 3': 'collector_last_name3',
                    'collector_first_name 4': 'collector_first_name4',
                    'collector_middle_name 4': 'collector_middle_name4',
                    'collector_last_name 4': 'collector_last_name4',
                    'collector_first_name 5': 'collector_first_name5',
                    'collector_middle_name 5': 'collector_middle_name5',
                    'collector_last_name 5': 'collector_last_name5',
                    'Genus': 'Genus',
                    'Species': 'Species',
                    'Qualifier': 'Qualifier',
                    'Hybrid': 'Hybrid',
                    'Taxon ID': 'RankID',
                    'Author': 'Author',
                    'Locality': 'locality',
                    'Verbatim Date': 'verbatim_date',
                    'Start Date': 'start_date',
                    'End Date': 'end_date'
                    }

        self.record_full = self.record_full.rename(columns=col_dict)

    # under this point column transformations will be done through a series of functions
    # will reuse/modify some wrangling functions from data standardization

    def col_clean(self):
        """will reformat and clean dataframe columns until ready for upload.
           **Still need format end-goal
        """
        self.record_full['verbatim_date'] = self.record_full['verbatim_date'].apply(replace_apostrophes)
        date_col_list = ['start_date', 'end_date']
        for col_string in date_col_list:
            self.record_full[col_string] = pd.to_datetime(self.record_full[col_string],
                                                          format='%m/%d/%Y').dt.strftime('%Y-%m-%d')




    # after file is wrangled into clean importable form,
    # and QC protocols to follow before import
    # QC measures needed here ? before proceeding.

    # In my opinion it is faster to make booleans now, and filter later in the process function,
    # but open to alterantive solutions

    def barcode_has_record(self):
        """check if barcode / catalog number already in collectionobject table"""
        self.record_full['CatalogNumber'] = self.record_full['CatalogNumber'].apply(remove_non_numerics)
        self.record_full['CatalogNumber'] = self.record_full['CatalogNumber'].astype(str)
        self.record_full['barcode_present'] = None
        for index, row in self.record_full.iterrows():
            barcode = os.path.basename(row['CatalogNumber'])
            barcode = barcode.zfill(9)
            sql = f"select CatalogNumber from casbotany.collectionobject " \
                  f"where CatalogNumber = {barcode};"
            db_barcode = self.specify_db_connection.get_one_record(sql)
            if db_barcode is None:
                row['barcode_present'] = False
            else:
                row['barcode_present'] = True

    def image_has_record(self):
        """checks if image name/barcode already on attachments table"""
        self.record_full['image_present'] = None
        for index, row in self.record_full.iterrows():
            file_name = os.path.basename(row['image_path'])
            file_name = file_name.lower()
            file_name = file_name.rsplit(".", 1)[0]
            sql = f'''select title from casbotany.attachment
                      where title = "{file_name}"'''
            db_name = self.specify_db_connection.get_one_record(sql)
            if db_name is None:
                row['image_present'] = True
            else:
                row['image_present'] = False

    def check_barcode_match(self):
        """checks if filepath barcode matches catalog number barcode"""
        self.record_full['file_path_digits'] = self.record_full['image_path'].apply(
            lambda path: self.get_first_digits_from_filepath(path, field_size=9)
        )
        self.record_full['is_barcode_match'] = self.record_full.apply(lambda row: row['file_path_digits'] ==
                                                                      row['CatalogNumber'].zfill(9), axis=1)

        self.record_full = self.record_full.drop(columns='file_path_digits')

    def check_if_images_present(self):
        """checks that each image exists, creating boolean column for later use"""
        self.record_full['image_valid'] = self.record_full['image_path'].apply(self.check_for_valid_image)

    # think of finding way to make this function logic not so repetitive
    def create_file_list(self):
        """creates a list of imagepaths and barcodes for upload,
        after checking conditions established to prevent overwriting data functions"""

        for index, row in self.record_full.iterrows():
            if not row['image_valid']:
                raise ValueError(f"image {row['image_path']} is not valid ")

            elif not row['is_barcode_match']:
                raise ValueError(f"image barcode {row['image_path']} does not match "
                                 f"{row['CatalogNumber']}")

            elif row['barcode_present'] and row['image_present']:
                raise ValueError(f"record {row['CatalogNumber']} and image {row['image_path']} "
                                 f"already in database")

            elif row['barcode_present'] and not row['image_present']:
                self.logger.debug(f"record {row['CatalogNumber']} "
                                  f"already in database, appending image")
                self.image_list.append(row['image_path'])

            elif not row['barcode_present'] and row['image_present']:
                self.logger.debug(f"image {row['image_path']} "
                                  f"already in database, appending record")
                self.barcode_list.append(row['CatalogNumber'])

            else:
                self.image_list.append(row['image_path'])
                self.barcode_list.append(row['CatalogNumber'])
            # a stopping point, to allow user to read logger messages,
            # and decide whether to proceed


    # will change row references to numeric index
    def create_agent_list(self, row):
        """creates a list of collectors that will be checked and added to agent/collector tables"""
        self.collector_list = []
        column_names = list(self.record_full.columns)
        for i in range(1, 6):
            try:
                first = column_names.index(f'collector_first_name{i}')
                middle = column_names.index(f'collector_middle_name{i}')
                last = column_names.index(f'collector_last_name{i}')
            except ValueError:
                break
            if pd.isna(row[first]) is False and pd.isna(row[last]) is False:
                sql = f'''SELECT AgentID FROM casbotany.agent WHERE FirstName = "{row[first]}"
                         AND LastName = "{row[last]}";'''
                agent_id = self.specify_db_connection.get_one_record(sql)
                if agent_id is None:
                    collector_dict = {f'collector_first_name': row[first],
                                      f'collector_middle_name': row[middle],
                                      f'collector_last_name': row[last]}
                    self.collector_list.append(collector_dict)

    # check after getting real dataset, still not final
    def taxon_concat(self, row):
        """taxon_concat:
                parses taxon columns to check taxon database, adds the Genus species, ranks, and Epithets,
                in the correct order, to create new taxon fullname in self.fullname. so that can be used for
                database checks.
            args:
                row: a row from a csv file containing taxon information with correct column names

        """
        hyb_index = self.record_full.columns.get_loc('Hybrid')
        rank_index = self.record_full.columns.get_loc('Rank 1')
        hyb_level = self.record_full.columns.get_loc('Hybrid Level')
        self.full_name = ""
        if row[hyb_index] is False:
            columns = ['Genus', 'Species', 'Rank 1', 'Epithet 1', 'Rank 2', 'Epithet 2']
            if row[rank_index] == 'Species':
                columns = ['Genus', 'Species', 'Rank 2', 'Epithet 2']
        else:
            columns = ['Hybrid Genus', 'Hybrid Species', 'Hybrid Level', 'Hybrid Epithet']
            if row[hyb_level] == 'Species':
                columns = ['Hybrid Genus', 'Hybrid Species']

        for column in columns:
            index = self.record_full.columns.get_loc(column)
            if row[index]:
                self.full_name += f" {row[index]}"

        # stripping leading and trailing space.
        self.full_name = self.full_name.lstrip()
        self.full_name = self.full_name.rstrip()
        # creating taxon name
        taxon_strings = self.full_name.split()
        self.tax_name = taxon_strings[-1]


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
                       'end_date', 'collector_number', 'locality', 'county', 'state', 'country']
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
        self.collecting_event_guid = uuid4()
        self.locality_guid = uuid4()
        self.geography_string = str(row[index_list[6]]) + ", " + \
                                str(row[index_list[7]]) + ", " + str(row[index_list[8]])
        self.sql_concat = ""

        # Locality create
        sql = f'''SELECT GeographyID FROM casbotany.geography 
                  WHERE `FullName` = "{self.geography_string}";'''
        self.GeographyID = self.specify_db_connection.get_one_record(sql)

        sql = f'''SELECT LocalityID FROM casbotany.locality 
                  WHERE `LocalityName`="{self.locality}";'''
        self.locality_id = self.specify_db_connection.get_one_record(sql)

        sql = f'''SELECT CollectingEventID FROM casbotany.collectingevent 
                  WHERE StationFieldNumber="{self.collector_number}";'''

        self.collecting_event_id = self.specify_db_connection.get_one_record(sql)


    def create_sql_string(self, col_list, val_list, tab_name):
        """create_sql_string:
               creates a new sql insert statement given a list of db columns,
               and values to input. Appends new statement to self.sql_concat
               to form new multi-statement query.
            args:
                col_list: list of database table columns to fill
                val_list: list of values to input into each table
                tab_name: name of the table you wish to insert data into
        """
        # removing brackets, making sure comma is not inside of quotations
        column_list = ', '.join(col_list)
        value_list = ', '.join(f"'{value}'" if isinstance(value, str) else repr(value) for value in val_list)


        sql = f'''INSERT INTO casbotany.{tab_name} ({column_list}) VALUES({value_list});'''

        self.sql_concat += sql


    def create_table_record(self, sql, is_test=False):
        """create_table_record:
               general code for the inserting of a new record into any table on casbotany.
               creates connection, and runs sql query. cursor.execute with arg multi, to
               handle multi-query commands.
           args:
               sql: the verbatim sql string, or multi sql query string to send to database
               is_test: set to False as default, if switched to true,
                        uses sql-lite database instead for testing

        """
        if is_test is True:
            connection = sqlite3.connect('cas_botanylite.db')
            cursor = connection.cursor()
        else:
            cursor = self.specify_db_connection.get_cursor()

        self.logger.info(f'running query: {sql}')
        self.logger.debug(sql)
        try:
            cursor.execute(sql, multi=True)
        except Exception as e:
            print(f"Exception thrown while processing sql: {sql}\n{e}\n", flush=True)
            self.logger.error(traceback.format_exc())
        if is_test is True:
            connection.commit()
            cursor.close()
            connection.close()
        else:
            self.specify_db_connection.commit()
            cursor.close()


    # need to review locality data strategy(want to upload locality datat without lat/long, or upload with?
    def append_locality_record(self):
        """append_locality_record:
               creates sql query to create new locality record if not already present in database,
               appends sql string to mult-query string sql_concat
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

        value_list = [f"{time_utils.get_pst_time_now_string()}",
                      f"{time_utils.get_pst_time_now_string()}",
                      1,
                      f"{self.locality_guid}",
                      0,
                      0,
                      f"{self.locality}",
                      3,
                      f"{self.GeographyID}",
                      f"{self.created_by_agent}",
                      f"{self.created_by_agent}"]

        self.create_sql_string(tab_name=table, col_list=column_list,
                               val_list=value_list)

    def append_agent_id(self):
        """append_agent_id:
               creates sql query to add new agent ids for missing agents,
               that are not already in DB, appends sql to the  mult-query sql
               string sql_concat
        """

        table = 'agent'
        for name_dict in self.collector_list:
            print(name_dict)
            self.agent_guid = uuid4()

            column_list = ['TimestampCreated',
                           'TimestampModified',
                           'Version',
                           'AgentType',
                           'DateOfBirthPrecision',
                           'DateOfDeathPrecision',
                           'FirstName',
                           'LastName',
                           'MiddleInitial',
                           'DivisionID',
                           'GUID',
                           'ModifiedByAgentID',
                           'CreatedByAgentID']

            value_list = [f"{time_utils.get_pst_time_now_string()}",
                          f"{time_utils.get_pst_time_now_string()}",
                          1,
                          1,
                          1,
                          1,
                          f"{name_dict['collector_first_name']}",
                          f"{name_dict['collector_last_name']}",
                          f"{name_dict['collector_middle_name']}",
                          2,
                          f"{self.agent_guid}",
                          f"{self.created_by_agent}"
                          f"{self.created_by_agent}"
                          ]

            self.create_sql_string(tab_name=table, col_list=column_list,
                                   val_list=value_list)
            # sql = '''SELECT AgentID from agent WHERE GUID = {self.agent_guid}'''
            # result = self.specify_db_connection.get_one_record(sql)
            # self.agent_guid_list.append(result)

    # is this needed?, does a collectorID need to be added for each sample?
    def append_collectingevent(self):
        """append_collecting_event:
               creates sql code for collectingevent table,
               appends new collectingevent sql to the multi-query sql string sql_concat,
               for each row.
        """

        # repulling locality id to reflect update
        sql = f'''select LocalityID from casbotany.locality where `LocalityName`="{self.locality}"'''

        self.locality_id = self.specify_db_connection.get_one_record(sql)

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

        value_list = [f"{time_utils.get_pst_time_now_string()}",
                      f"{time_utils.get_pst_time_now_string()}",
                      0,
                      f"{self.collecting_event_guid}",
                      3,
                      f"{self.collector_number}",
                      f"{self.verbatim_date}",
                      f"{self.start_date}",
                      f"{self.end_date}",
                      f"{self.locality_id}",
                      f"{self.created_by_agent}",
                      f"{self.created_by_agent}"]

        self.create_sql_string(tab_name=table, col_list=column_list,
                               val_list=value_list)


    # def append_taxon(self):
    #     table = "taxon"
    #
    #     columns = ['TaxonID', 'TimestampCreated', 'Version',
    #                'Author', 'FullName', 'GUID', 'HighestChildNodeNumber',
    #                'IsAccepted', 'IsHybrid', 'Name', 'NodeNumber', 'RankID',
    #                'TaxonTreeDefID', 'ParentID', 'ModifiedByAgentID',
    #                'CreatedByAgentID', 'TaxonTreeDegItemID']

    def append_collection_object(self):
        """append_collection_object:
               creates sql code for collection object table,
               appends new collection_object sql to the multi-query sql string sql_concat,
               for each row.
        """
        # will new collecting event ids need to be created ?
        # repulling collecting event id to relect new record
        sql = f'''select CollectingEventID from casbotany.collectingevent
                  where guid="{self.collecting_event_guid}"'''

        self.collecting_event_id = self.specify_db_connection.get_one_record(sql)

        table = 'collectionobject'


        column_list = ['TimestampCreated',
                       'TimestampModified',
                       'CollectingEventID',
                       'Version',
                       'CollectionMemberID',
                       'CatalogNumber',
                       'CatalogedDatePrecision',
                       'GUID',
                       'CollectionID',
                       'Date1Precision',
                       'InventoryDatePrecision',
                       'ModifiedByAgentID',
                       'CreatedByAgentID'
                       ]

        value_list = [f"{time_utils.get_pst_time_now_string()}",
                      f"{time_utils.get_pst_time_now_string()}",
                      f"{self.collecting_event_id}",
                      0,
                      4,
                      f"{self.barcode}",
                      1,
                      f"{uuid4()}",
                      4,
                      1,
                      1,
                      f"{self.created_by_agent}",
                      f"{self.created_by_agent}"]

        self.create_sql_string(val_list=value_list, col_list=column_list, tab_name=table)

    # def purge_records(self, error, layers: int):
    #     tabs = ['locality', 'agent', 'collectingevent', 'collectionobject'][:layers]
    #     guid_string = [self.locality_id, self.agent_guid, self.collecting_event_guid,
    #                    self.barcode]
    #
    #     cursor = self.specify_db_connection.get_cursor()
    #
    #     for index, table in enumerate(tabs):
    #         print(f"Purging {guid_string[index]} from {table}")
    #
    #         if isinstance(guid_string[index], list):
    #             guid_list = ', '.join(guid_string[index])
    #             sql = f'''DELETE FROM {table} WHERE GUID IN ({guid_list};)'''
    #         else:
    #             sql = f'''DELETE FROM {table} WHERE GUID = "{guid_string[index]};" '''
    #
    #         self.logger.info(f'running query: {sql}')
    #
    #         cursor.execute(sql)
    #
    #         self.specify_db_connection.commit()
    #
    #         cursor.close()
    #
    #     sys.exit(f"Terminating script: {error}")


    def cont_prompter(self):
        """cont_prompter:
                placed critical step after database checks, prompts users to
                confirm in order to continue. Allows user to check logger texts to make sure
                no unwanted data is being uploaded.
        """
        while True:
            user_input = input("Do you want to continue? (y/n): ")
            if user_input.lower() == "y":
                break
            elif user_input.lower() == "n":
                sys.exit("Script terminated by user.")
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

    def upload_records(self):
        """upload_records:
               an ensemble function made up of all row level, and database functions,
               loops through each row of the csv, updates the global values, and creates new table records
           args:
                none
            returns:
                new table records related
        """
        self.record_full = self.record_full[self.record_full['CatalogNumber'].isin(self.barcode_list)]
        for index, row in self.record_full.iterrows():
            self.create_agent_list(row)
            self.taxon_concat(row)
            self.populate_fields(row)
            print(self.collector_list)

            if self.locality_id is None:
                self.append_locality_record()

            if len(self.collector_list) > 0:
                self.append_agent_id()

            if self.collecting_event_id is None:
                self.append_collectingevent()

            self.append_collection_object()

            print(self.sql_concat)

            try:
                self.create_table_record(sql=self.sql_concat)
            except Exception as e:
                self.logger.error(f"sql error: {e}")
                sys.exit("terminating script")

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
        folder_path = f'picturae_img/{self.date_use}{sla}'
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
        """
        sla = os.path.sep
        folder_path = f'picturae_img/{self.date_use}{sla}'
        prefix = ".hidden_"  # The prefix added during hiding
        for file_name in os.listdir(folder_path):
            if file_name.startswith(prefix):
                old_file_name = file_name[len(prefix):]
                old_file_path = os.path.join(folder_path, old_file_name)
                new_file_path = os.path.join(folder_path, file_name)
                os.rename(new_file_path, old_file_path)

    def upload_attachments(self):
        """upload_attachments:
                this function calls client tools, in order to add
                attachments in image list. Updates date in
                botany_importer_config to ensure prefix is
                updated for correct filepath

        """

        filename = "botany_importer_config.py"

        with open(filename, 'r') as file:
            # Read the contents of the file
            content = file.read()
        date_rep = self.date_use
        # Replace the string
        new_content = re.sub(r'\bdate_str = \w*\b', date_rep, content)

        with open(filename, 'w') as file:
            # Write the modified content back to the file
            file.write(new_content)

        try:
            self.hide_unwanted_files()

            os.system('cd /Users/mdelaroca/Documents/sandbox_db/specify-sandbox/web-asset-server/image_client')

            os.system('python client_tools.py Botany import')

            self.unhide_files()
        except Exception as e:
            self.logger.error(f"{e}")
        # except Exception as e:
        #     self.purge_records(error=e, layers=4)
        #     sys.exit('error in attachments, terminating script')

    def run_all_methods(self):
        """run_all_methods:
                        self-explanatory function, will run all function in class in sequential manner"""

        # create test images comment out when running for real.

        # date_string = "2023-06-28"
        # image = Image.new('RGB', (200, 200), color='red')

        # barcode_list = [999999981, 999999982, 999999983]
        # for barcode in barcode_list:
        #     expected_image_path = f"picturae_img/{date_string}/CAS{barcode}.JPG"
        #     os.makedirs(os.path.dirname(expected_image_path), exist_ok=True)
        #     print(f"Created directory: {os.path.dirname(expected_image_path)}")
        #     image.save(expected_image_path)

        # setting directory
        self.to_current_directory()
        # verifying file presence
        self.file_present()
        # merging csv files
        self.csv_merge()
        # renaming columns
        self.csv_colnames()
        # cleaning data
        self.col_clean()

        # checking if barcode record present in database
        self.barcode_has_record()

        # checking if barcode has valid image file
        self.check_if_images_present()

        # checking if image has record
        self.image_has_record()
        # checking if barcode has valid file name for barcode
        self.check_barcode_match()

        # creating file list after conditions
        self.create_file_list()

        # prompt
        self.cont_prompter()

        # uploading csv records
        self.upload_records()

        # uploading attachments
        self.upload_attachments()

        self.logger.info("process finished")


def master_run(date_string):
    DataOnboard_int = DataOnboard(date_string=date_string)
    DataOnboard_int.run_all_methods()


master_run(date_string="2023-06-28")
