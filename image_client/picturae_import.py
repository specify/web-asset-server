"""this file will be used to parse the data from Picturae into an uploadable format to Specify"""

import atexit

import pandas as pd
from rpy2 import robjects
from rpy2.robjects import pandas2ri
import time_utils
from uuid import uuid4
from data_utils import *
from casbotany_sql_lite import *
from datetime import date
from datetime import datetime
import logging
from sql_csv_utils import *
from importer import Importer

upload_time = datetime.now()


def time_stamper():
    # marking starting time stamp
    starting_time_stamp = datetime.now()

    # at exit run ending timestamp and append timestamp csv
    atexit.register(create_timestamps, start_time=starting_time_stamp)

class DataOnboard(Importer):
    """DataOnboard:
           A class with methods designed to wrangle, verify,
           and upload a csv file containing transcribed
           specimen sheet records into the casbotany database,
           along with attached images
    """
    def __init__(self, date_string):
        super().__init__(picturae_config, "Botany")
        self.date_use = date_string
        self.logger = logging.getLogger('DataOnboard')
        # full collector list is for populating existing and missing agents into collector table
        # new_collector_list is only for adding new agents to agent table.
        # manual taxon list, list of skipped taxons to be manually verified
        empty_lists = ['barcode_list', 'image_list', 'full_collector_list', 'new_collector_list',
                       'new_taxon_list']

        for empty_list in empty_lists:
            setattr(self, empty_list, [])

        self.manual_taxon_dict = {}
        self.no_match_dict = {}

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

    def file_present(self):
        """file_present:
           checks if correct filepath in working directory,
           checks if file is on input date
           checks if file folder is present.
           uses self.use_date to decide which folders to check
           args:
                none
        """

        to_current_directory()

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
        """csv_merge:
                merges the folder_csv and the specimen_csv on barcode
           args:
                fold_csv: folder level csv to be input as argument for merging
                spec_csv: specimen level csv to be input as argument for merging
        """
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
        """csv_colnames: function to be used to rename columns to specify standards. includes csv)_
           args:
                none"""
        # remove columns !! review when real dataset received

        cols_drop = ['application_batch', 'csv_batch', 'object_type', 'filed_as_family',
                     'barcode_info', 'Notes', 'Feedback']

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

    def taxon_concat(self, row):
        """taxon_concat:
                parses taxon columns to check taxon database, adds the Genus species, ranks, and Epithets,
                in the correct order, to create new taxon fullname in self.fullname. so that can be used for
                database checks.
            args:
                row: a row from a csv file containing taxon information with correct column names

        """
        hyb_index = self.record_full.columns.get_loc('Hybrid')
        full_name = ""
        tax_name = ""
        gen_spec = ""
        if row[hyb_index] is False:
            columns1 = ['Genus', 'Species', 'Rank 1', 'Epithet 1', 'Rank 2', 'Epithet 2']
            columns2 = ['Genus', 'Species']
        else:
            columns1 = ['Hybrid Genus', 'Hybrid Species', 'Hybrid Rank 1', 'Hybrid Epithet 1']
            columns2 = ['Hybrid Genus', 'Hybrid Species']

        for column in columns1:
            index = self.record_full.columns.get_loc(column)
            if pd.notna(row[index]):
                full_name += f" {row[index]}"

        for column in columns2:
            index = self.record_full.columns.get_loc(column)
            if pd.notna(row[index]):
                gen_spec += f" {row[index]}"


        full_name = full_name.strip()
        gen_spec = gen_spec.strip()
        # creating taxon name
        taxon_strings = full_name.split()
        tax_name = taxon_strings[-1]

        return str(gen_spec), str(full_name), str(tax_name)


    def taxon_assign_defitem(self,taxon_string):

        if " f. " in taxon_string:
            return 17, 260
        elif "subf." in taxon_string:
            return 21, 270
        elif "subvar." in taxon_string:
            return 16, 250
        elif "var." in taxon_string:
            return 15, 240
        elif "subsp." in taxon_string:
            return 14, 230
        elif len(taxon_string.split()) == 1:
            return 12, 180
        else:
            return 13, 220


    def check_single_taxa(self, taxon_name, barcode):
        """check_single_taxa: designed to take in one taxaname and
           do a TNRS operation on it to get an author for iterative higher taxa"""
        taxon_frame = {"barcodes": [barcode], "fullname": [taxon_name]}

        taxon_frame = pd.DataFrame(taxon_frame)

        pandas2ri.activate()

        r_dataframe_tax = pandas2ri.py2rpy(taxon_frame)

        robjects.globalenv['r_dataframe_taxon'] = r_dataframe_tax

        with open('taxon_check/test_TNRS.R', 'r') as file:
            r_script = file.read()

        robjects.r(r_script)

        resolved_taxon = robjects.r['resolved_taxa']

        resolved_taxon = robjects.conversion.rpy2py(resolved_taxon)

        taxon_list = list(resolved_taxon['accepted_author'])

        self.parent_author = taxon_list[0]


    def taxon_check_real(self):
        bar_tax = self.record_full[['CatalogNumber', 'fullname']]

        pandas2ri.activate()

        r_dataframe_tax = pandas2ri.py2rpy(bar_tax)

        robjects.globalenv['r_dataframe_taxon'] = r_dataframe_tax

        with open('taxon_check/test_TNRS.R', 'r') as file:
            r_script = file.read()

        robjects.r(r_script)

        resolved_taxon = robjects.r['resolved_taxa']

        resolved_taxon = robjects.conversion.rpy2py(resolved_taxon)

        self.record_full = pd.merge(self.record_full, resolved_taxon, on="fullname", how="left")

        upload_length = len(self.record_full.index)

        # dropping taxon rows with no match

        self.record_full = self.record_full.dropna(subset=['name_matched'])

        clean_length = len(self.record_full.index)

        records_dropped = upload_length-clean_length

        if records_dropped != 0:
            self.logger.info(f"{records_dropped} rows dropped due to taxon errors")

        self.record_full = separate_qualifiers(self.record_full, tax_col='fullname')



    def col_clean(self):
        """will reformat and clean dataframe columns until ready for upload.
           **Still need format end-goal
        """
        self.record_full['verbatim_date'] = self.record_full['verbatim_date'].apply(replace_apostrophes)
        self.record_full['locality'] = self.record_full['locality'].apply(replace_apostrophes)
        date_col_list = ['start_date', 'end_date']
        for col_string in date_col_list:
            self.record_full[col_string] = pd.to_datetime(self.record_full[col_string],
                                                          format='%m/%d/%Y').dt.strftime('%Y-%m-%d')

        self.record_full[['gen_spec', 'fullname', 'taxname']] = self.record_full.apply(self.taxon_concat,
                                                                           axis=1, result_type='expand')

        # setting datatypes for columns
        string_list = self.record_full.columns.to_list()

        self.record_full[string_list] = self.record_full[string_list].astype(str)

        self.record_full = self.record_full.replace(['', None, 'nan', np.nan], pd.NA)






    # will split file into two files
    # after file is wrangled into clean importable form,
    # and QC protocols to follow before import
    # QC measures needed here ? before proceeding.

    # In my opinion it is faster to make booleans now, and filter later in the process function,
    # but open to alternative solutions

    def barcode_has_record(self):
        """check if barcode / catalog number already in collectionobject table"""
        self.record_full['CatalogNumber'] = self.record_full['CatalogNumber'].apply(remove_non_numerics)
        self.record_full['CatalogNumber'] = self.record_full['CatalogNumber'].astype(str)
        self.record_full['barcode_present'] = ''

        for index, row in self.record_full.iterrows():
            barcode = os.path.basename(row['CatalogNumber'])
            barcode = barcode.zfill(9)
            sql = f'''select CatalogNumber from collectionobject
                      where CatalogNumber = {barcode};'''
            db_barcode = self.specify_db_connection.get_one_record(sql)
            if db_barcode is None:
                self.record_full.loc[index, 'barcode_present'] = False
            else:
                self.record_full.loc[index, 'barcode_present'] = True

    def image_has_record(self):
        """checks if image name/barcode already on attachments table"""
        self.record_full['image_present'] = None
        for index, row in self.record_full.iterrows():
            file_name = os.path.basename(row['image_path'])
            file_name = file_name.lower()
            file_name = file_name.rsplit(".", 1)[0]
            sql = f'''select title from attachment
                      where title = "{file_name}";'''
            db_name = self.specify_db_connection.get_one_record(sql)
            if db_name is None:
                self.record_full.loc[index, 'image_present'] = False
            else:
                self.record_full.loc[index, 'image_present'] = True

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

        print(os.getcwd())

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
                self.logger.warning(f"record {row['CatalogNumber']} and image {row['image_path']}"
                                    f"already in database")

            elif row['barcode_present'] and not row['image_present']:
                self.logger.warning(f"record {row['CatalogNumber']} "
                                    f"already in database, appending image")
                self.image_list.append(row['image_path'])

            elif not row['barcode_present'] and row['image_present']:
                self.logger.warning(f"image {row['image_path']} "
                                    f"already in database, appending record")
                self.barcode_list.append(row['CatalogNumber'])

            else:
                self.image_list.append(row['image_path'])
                self.barcode_list.append(row['CatalogNumber'])

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


                sql = create_name_sql(first_name, last_name, middle, title)

                agent_id = self.specify_db_connection.get_one_record(sql)

                collector_dict = {f'collector_first_name': first_name,
                                  f'collector_middle_initial': middle,
                                  f'collector_last_name': last_name,
                                  f'collector_title': title}

                self.full_collector_list.append(collector_dict)
                if agent_id is None:
                    self.new_collector_list.append(collector_dict)

    # check after getting real dataset, still not final

    def populate_sql(self, tab_name, id_col, key_col, match, match_type=str):
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
        if match_type == str:
            sql = f'''SELECT {id_col} FROM {tab_name} WHERE `{key_col}` = "{match}";'''
        elif match_type == int:
            sql = f'''SELECT {id_col} FROM {tab_name} WHERE `{key_col}` = {match}'''

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
                       'end_date', 'collector_number', 'locality', 'county', 'state', 'country', 'fullname', 'taxname',
                       'gen_spec', 'qualifier', 'name_matched', 'Genus', 'Family', 'Hybrid', 'accepted_author']
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
        self.full_name = row[index_list[9]]
        self.tax_name = row[index_list[10]]
        self.gen_spec = row[index_list[11]]
        self.qualifier = row[index_list[12]]
        self.name_matched = row[index_list[13]]
        self.genus = row[index_list[14]]
        self.family_name = row[index_list[15]]
        self.is_hybrid = row[index_list[16]]
        self.author = row[index_list[17]]

        guid_list = ['collecting_event_guid', 'collection_ob_guid', 'locality_guid', 'determination_guid']
        for guid_string in guid_list:
            setattr(self, guid_string, uuid4())

        self.geography_string = str(row[index_list[6]]) + ", " + \
                                str(row[index_list[7]]) + ", " + str(row[index_list[8]])

        self.GeographyID = self.populate_sql(tab_name='geography', id_col='GeographyID',
                                             key_col='FullName', match=self.geography_string)
        self.locality_id = self.populate_sql(tab_name='locality', id_col='LocalityID',
                                             key_col='LocalityName', match=self.locality)

    def taxon_get(self, name):
        sql = f'''SELECT TaxonID FROM taxon WHERE FullName = "{name}";'''
        id = self.specify_db_connection.get_one_record(sql)
        return id

    def populate_taxon(self):
        """populate taxon: creates a taxon list, which checks different rank levels in the taxon,
        as genus must be uploaded before species , before subtaxa etc.."""

        self.taxon_list = []
        self.taxon_id = self.taxon_get(name=self.full_name)
        # append taxon full name
        if self.taxon_id is None:
            self.taxon_list.append(self.full_name)
            # check base name if base name differs e.g. if var. or subsp.
            if self.full_name != self.gen_spec:
                self.gen_spec_id = self.taxon_get(name=self.gen_spec)
                self.check_single_taxa(taxon_name=self.gen_spec, barcode=self.barcode)
                # adding base name to taxon_list
                if self.gen_spec_id is None:
                    self.taxon_list.append(self.gen_spec)

            # base value for gen spec is set as None so will work either way.
            # checking for genus id
            if self.gen_spec_id is None:
                self.genus_id = self.taxon_get(name=self.genus)

                # adding genus name if missing
                if self.genus_id is None:
                    self.taxon_list.append(self.genus)

                    # checking family id
                    self.family_id = self.taxon_get(name=self.family_name)
                    # adding family name to list
                    if self.family_id is None:
                        self.taxon_list.append(self.family_name)
        else:
            pass

    def create_table_record(self, sql, is_test=False):
        """create_table_record:
               general code for the inserting of a new record into any table on casbotany.
               creates connection, and runs sql query. cursor.execute with arg multi, to
               handle multi-query commands.
           args:
               sql: the verbatim sql string, or multi sql query string to send to database
               is_test: set to False as default, if switched to true,
                        uses sql-lite database instead for testing.
        """
        if is_test is True:
            connection = sqlite3.connect('cas_botanylite.db')
            cursor = connection.cursor()
        else:
            cursor = self.specify_db_connection.get_cursor()

        self.logger.info(f'running query: {sql}')
        self.logger.debug(sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f"Exception thrown while processing sql: {sql}\n{e}\n", flush=True)
            self.logger.error(traceback.format_exc())
        if is_test is True:
            connection.commit()
            cursor.close()
            connection.close()
        else:
            try:
                self.specify_db_connection.commit()

            except Exception as e:
                self.logger.error(f"sql debug: {e}")
                sys.exit("terminating script")

            cursor.close()

    def create_locality_record(self):
        """create_locality_record:
               defines column and value list , runs them as args through create_sql_string and create_table record
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

        sql = create_sql_string(tab_name=table, col_list=column_list,
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

            sql = create_sql_string(tab_name=table, col_list=columns,
                                    val_list=values)

            self.create_table_record(sql=sql)

    def create_collectingevent(self):
        """create_collectingevent:
                defines column and value list , runs them as
                args through create_sql_string and create_table record
                in order to add new collectingevent record to database.
         """

        # repulling locality id to reflect update

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

        sql = create_sql_string(tab_name=table, col_list=column_list,
                                val_list=value_list)

        self.create_table_record(sql=sql)

    # temporarily creating exception list until reliable taxon protocol
    def create_taxon(self):
        """create_taxon: populates the taxon table iteratively by adding higher taxa first,
                            before lower taxa"""
        # for now do not upload
        parent_list = [self.full_name, self.gen_spec, self.genus, self.family_name]

        if self.gen_spec == self.full_name:
            parent_list.remove(self.gen_spec)

        for index, taxa_rank in reversed(list(enumerate(self.taxon_list))):

            taxon_guid = uuid4()
            rank_name = taxa_rank
            parent_id = self.taxon_get(name=parent_list[index+1])
            table = 'taxon'
            rank_parts = taxa_rank.split()
            rank_end = rank_parts[-1]
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

            boolean_value = bool(self.is_hybrid.lower() == "true")

            value_list = [f"{time_utils.get_pst_time_now_string()}",
                          f"{time_utils.get_pst_time_now_string()}",
                          1,
                          author_insert,
                          f"{rank_name}",
                          f"{taxon_guid}",
                          "World Checklist of Vascular Plants 2023",
                          True,
                          boolean_value,
                          f"{rank_end}",
                          f"{rank_id}",
                          1,
                          f"{parent_id}",
                          f"{self.created_by_agent}",
                          f"{self.created_by_agent}",
                          f"{tree_item_id}"
                          ]

            value_list, column_list = remove_two_index(value_list, column_list)

            sql = create_sql_string(tab_name=table, col_list=column_list,
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
                      f"{upload_time.strftime('%Y-%m-%d')}",
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

        sql = create_sql_string(tab_name=table, col_list=column_list,
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
                           # 'Qualifier',
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
                          f"{self.determination_guid}",
                          f"{self.taxon_id}",
                          f"{self.collection_ob_id}",
                          f"{self.created_by_agent}",
                          f"{self.created_by_agent}",
                          f"{self.taxon_id}",
                          ]

            # removing na values from both lists
            value_list, column_list = remove_two_index(value_list, column_list)

            sql = create_sql_string(tab_name=table, col_list=column_list,
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

            sql = create_name_sql(first_name=agent_dict["collector_first_name"],
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

            sql = create_sql_string(tab_name=table, col_list=column_list,
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

            self.create_collectingevent()

            self.create_collection_object()

            self.create_determination()

            self.create_collector()

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

    def run_all_methods(self):
        """run_all_methods:
                        self-explanatory function, will run all function in class in sequential manner"""
        # create_test_images(list(range(999999981, 999999985)), date_string=self.date_use)

        # setting directory
        to_current_directory()
        # verifying file presence
        self.file_present()
        # merging csv files
        self.csv_merge()
        # renaming columns
        self.csv_colnames()
        # cleaning data
        self.col_clean()

        self.taxon_check_real()



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
        cont_prompter()

        # starting purge timer
        time_stamper()

        # creating tables

        self.upload_records()

        # creating new taxon list
        if len(self.new_taxon_list) > 0:
            write_list_to_csv(f"picturae_csv/{self.date_use}/new_taxa_{date.today()}", self.new_taxon_list)

        # uploading attachments
        self.upload_attachments()

        write_dict_to_csv(tax_dict=self.manual_taxon_dict, filename=f"taxon_check/unmatched_taxa/"
                          f"manual_taxa_{self.date_use}.csv")
        # writing time stamps to txt file

        self.logger.info("process finished")


def master_run(date_string):
    dataonboard_int = DataOnboard(date_string=date_string)
    dataonboard_int.run_all_methods()


master_run(date_string="2023-06-28")
