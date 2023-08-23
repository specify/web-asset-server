"""picturae_csv_create: this file is for wrangling and creating the dataframe
   and csv with the correctly parsed fields for upload, in picturae_import"""

import picturae_config
from rpy2 import robjects
from rpy2.robjects import pandas2ri
from data_utils import *
import logging
from sql_csv_utils import *
from importer import Importer


class CsvCreatePicturae(Importer):
    def __init__(self, date_string):
        super().__init__(picturae_config, "Botany")
        self.date_use = date_string
        self.logger = logging.getLogger('DataOnboard')
        # full collector list is for populating existing and missing agents into collector table
        # new_collector_list is only for adding new agents to agent table.
        # manual taxon list, list of skipped taxa to be manually verified
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

        self.record_full.rename(columns=col_dict, inplace=True)

    def taxon_concat(self, row):
        """taxon_concat:
                parses taxon columns to check taxon database, adds the Genus species, ranks, and Epithets,
                in the correct order, to create new taxon fullname in self.fullname. so that can be used for
                database checks.
            args:
                row: a row from a csv file containing taxon information with correct column names

        """
        hyb_index = self.record_full.columns.get_loc('Hybrid')
        is_hybrid = row[hyb_index]

        full_name = ""
        tax_name = ""
        gen_spec = ""
        hybrid_base = ""

        if is_hybrid is True:
            gen_index = self.record_full.columns.get_loc('Hybrid Genus')
            genus = row[gen_index]
        else:
            gen_index = self.record_full.columns.get_loc('Genus')
            genus = row[gen_index]

        if is_hybrid is False:
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
        # creating temporary string in order to get tax order
        separate_string = remove_qualifiers(full_name)
        taxon_strings = separate_string.split()

        # changing name variable based on condition
        if is_hybrid is False:
            tax_name = taxon_strings[-1]
        else:
            if genus == full_name:
                tax_name = " ".join(taxon_strings[-2:])
            elif gen_spec == full_name and genus != full_name:
                tax_name = " ".join(taxon_strings[-3:])
                tax_name = tax_name.lower()
            else:
                tax_name = extract_after_subtax(separate_string)
                tax_name = tax_name.lower()
        if is_hybrid is True:
            if ("var." in full_name or "subsp." in full_name or " f." in full_name or "subf." in full_name) \
                 and len(taxon_strings) < 8:
                hybrid_base = full_name
                full_name = " ".join(taxon_strings[:2])
                # will have to revisit this when actual data recieved ,
                # although this kind of cross is extremely rare Gen spec var. a x Gen spec var. b
            elif ("var." in full_name or "subsp." in full_name or " f." in full_name or "subf." in full_name) \
                    and len(taxon_strings) >= 8:
                hybrid_base = full_name
                full_name = taxon_strings[0]
            else:
                hybrid_base = full_name
                full_name = taxon_strings[0]

        return str(gen_spec), str(full_name), str(tax_name), str(hybrid_base)

    def taxon_check_real(self):
        """Sends the concatenated taxon column, through TNRS, to match names,
           with and without spelling mistakes, """
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

        records_dropped = upload_length - clean_length

        if records_dropped != 0:
            self.logger.info(f"{records_dropped} rows dropped due to taxon errors")

        # re-consolidating hybrid column to fullname and removing hybrid_base column
        hybrid_mask = self.record_full['hybrid_base'].notna()

        self.record_full.loc[hybrid_mask, 'fullname'] = self.record_full.loc[hybrid_mask, 'hybrid_base']

        self.record_full.drop(columns=['hybrid_base'])

        # executing qualifier separator function

        self.record_full = separate_qualifiers(self.record_full, tax_col='fullname')

        self.record_full['gen_spec'] = self.record_full['gen_spec'].apply(remove_qualifiers)

        print(self.record_full)

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

        self.record_full[['gen_spec', 'fullname',
                          'taxname', 'hybrid_base']] = self.record_full.apply(self.taxon_concat,
                                                                              axis=1, result_type='expand')

        # setting datatypes for columns
        string_list = self.record_full.columns.to_list()

        self.record_full[string_list] = self.record_full[string_list].astype(str)

        self.record_full = self.record_full.replace(['', None, 'nan', np.nan], pd.NA)

    def barcode_has_record(self):
        """check if barcode / catalog number already in collectionobject table"""
        self.record_full['CatalogNumber'] = self.record_full['CatalogNumber'].apply(remove_non_numerics)
        self.record_full['CatalogNumber'] = self.record_full['CatalogNumber'].astype(str)
        self.record_full['barcode_present'] = ''

        for index, row in self.record_full.iterrows():
            barcode = os.path.basename(row['CatalogNumber'])
            barcode = barcode.zfill(9)
            sql = f'''select CatalogNumber from casbotany.collectionobject
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
            sql = f'''select title from casbotany.attachment
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
                                                                      row['CatalogNumber'].zfill(9),
                                                                      axis=1)

        self.record_full = self.record_full.drop(columns='file_path_digits')

    def check_if_images_present(self):
        """checks that each image exists, creating boolean column for later use"""

        print(os.getcwd())

        self.record_full['image_valid'] = self.record_full['image_path'].apply(self.check_for_valid_image)

    def write_upload_csv(self):
        file_path = f"PIC_upload/PIC_record_{self.date_use}.csv"

        self.record_full.to_csv(file_path, index=False)

        print(f'DataFrame has been saved to csv as: {file_path}')

    def run_all(self):
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

        # writing csv for inspection and upload
        self.write_upload_csv()


def master_run(date_string):
    csv_create_int = CsvCreatePicturae(date_string=date_string)

    csv_create_int.run_all()


master_run(date_string="2023-06-28")
