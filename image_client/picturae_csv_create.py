"""picturae_csv_create: this file is for wrangling and creating the dataframe
   and csv with the parsed fields required for upload, in picturae_import.
   Uses TNRS (Taxonomic Name Resolution Service) in taxon_check/test_TNRS.R
   to catch spelling mistakes, mis-transcribed taxa.
   Source for taxon names at IPNI (International Plant Names Index): https://www.ipni.org/ """
from uuid import uuid4
import picturae_config
import logging
from taxon_parse_utils import *
from picturae_import_utils import *
from string_utils import *
from importer import Importer
from sql_csv_utils import *
from specify_db import SpecifyDb
import picdb_config

# creating a batch uuid
batch_uuid = uuid4()


starting_time_stamp = datetime.now()


class CsvCreatePicturae(Importer):
    def __init__(self, date_string, istesting=False):
        super().__init__(picturae_config, "Botany")
        self.date_use = date_string
        self.logger = logging.getLogger('DataOnboard')

        # setting up alternate db connection for batch database
        self.batch_db_connection = SpecifyDb(db_config_class=picdb_config)

        # intializing parameters for database upload
        init_list = ['taxon_id', 'barcode',
                     'collector_number', 'collecting_event_guid',
                     'collecting_event_id',
                     'determination_guid', 'collection_ob_id', 'collection_ob_guid',
                     'name_id', 'author_sci', 'family', 'gen_spec_id', 'family_id', 'parent_author']

        for param in init_list:
            setattr(self, param, None)

        if istesting is False:
            self.run_all()

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

        dir_path = picturae_config.DATA_FOLDER + f"{self.date_use}"

        dir_sub = os.path.isdir(dir_path)

        if dir_sub is True:
            folder_path = picturae_config.DATA_FOLDER + f"{self.date_use}" + picturae_config.CSV_FOLD + \
                          f"{self.date_use}" + ").csv"

            specimen_path = picturae_config.DATA_FOLDER + f"{self.date_use}" + picturae_config.CSV_SPEC + \
                            f"{self.date_use}" + ").csv"

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

            merge_len = len(self.record_full)

            self.record_full = self.record_full.drop_duplicates()

            unique_len = len(self.record_full)

            if merge_len > unique_len:
                raise ValueError(f"merge produced {merge_len-unique_len} duplicate records")

        else:
            raise ValueError("Barcode Columns do not match!")

    def csv_colnames(self):
        """csv_colnames: function to be used to rename columns to DB standards.
           args:
                none"""
        # remove columns !! review when real dataset received

        cols_drop = ['application_batch', 'csv_batch', 'object_type', 'filed_as_family',
                     'barcode_info', 'Notes', 'Feedback']

        self.record_full = self.record_full.drop(columns=cols_drop)

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

        # defining empty strings for parsed taxon substrings
        full_name = ""
        tax_name = ""
        first_intra = ""
        gen_spec = ""
        hybrid_base = ""

        gen_index = self.record_full.columns.get_loc('Genus')
        genus = row[gen_index]

        column_sets = [
            ['Genus', 'Species', 'Rank 1', 'Epithet 1', 'Rank 2', 'Epithet 2'],
            ['Genus', 'Species', 'Rank 1', 'Epithet 1'],
            ['Genus', 'Species']
        ]

        for columns in column_sets:
            for column in columns:
                index = self.record_full.columns.get_loc(column)
                if pd.notna(row[index]):
                    if columns == column_sets[0]:
                        full_name += f" {row[index]}"
                    elif columns == column_sets[1]:
                        first_intra += f" {row[index]}"
                    elif columns == column_sets[2]:
                        gen_spec += f" {row[index]}"

        full_name = full_name.strip()
        first_intra = first_intra.strip()
        gen_spec = gen_spec.strip()
        # creating taxon name
        # creating temporary string in order to parse taxon names without qualifiers
        separate_string = remove_qualifiers(full_name)
        taxon_strings = separate_string.split()

        second_epithet_in = row[self.record_full.columns.get_loc('Epithet 2')]
        first_epithet_in = row[self.record_full.columns.get_loc('Epithet 1')]
        spec_in = row[self.record_full.columns.get_loc('Species')]
        genus_in = row[self.record_full.columns.get_loc('Genus')]
        # changing name variable based on condition

        if not pd.isna(second_epithet_in):
            tax_name = remove_qualifiers(second_epithet_in)
        elif not pd.isna(first_epithet_in):
            tax_name = remove_qualifiers(first_epithet_in)
        elif not pd.isna(spec_in):
            tax_name = remove_qualifiers(spec_in)
        elif not pd.isna(genus_in):
            tax_name = remove_qualifiers(genus_in)
        else:
            return ValueError('missing taxon in row')

        if is_hybrid is True:
            if first_intra == full_name:
                if "var." in full_name or "subsp." in full_name or " f." in full_name or "subf." in full_name:
                    hybrid_base = full_name
                    full_name = " ".join(taxon_strings[:2])
                else:
                    hybrid_base = full_name
                    full_name = taxon_strings[0]
                    if full_name != genus:
                        full_name = " ".join(taxon_strings[:2])

            elif len(first_intra) != len(full_name):
                if "var." in full_name or "subsp." in full_name or " f." in full_name or "subf." in full_name:
                    hybrid_base = full_name
                    full_name = " ".join(taxon_strings[:4])
                else:
                    pass

        return str(gen_spec), str(full_name), str(first_intra), str(tax_name), str(hybrid_base)

    def taxon_check_real(self):
        """taxon_check_real:
           Sends the concatenated taxon column, through TNRS, to match names,
           with and without spelling mistakes, only checks base name
           for hybrids as IPNI does not work well with hybrids
           """

        from rpy2 import robjects
        from rpy2.robjects import pandas2ri

        bar_tax = self.record_full[['CatalogNumber', 'fullname']]

        pandas2ri.activate()

        r_dataframe_tax = pandas2ri.py2rpy(bar_tax)

        robjects.globalenv['r_dataframe_taxon'] = r_dataframe_tax

        with open('taxon_check/R_TNRS.R', 'r') as file:
            r_script = file.read()

        robjects.r(r_script)

        resolved_taxon = robjects.r['resolved_taxa']

        resolved_taxon = robjects.conversion.rpy2py(resolved_taxon)

        resolved_taxon['overall_score'].fillna(0, inplace=True)

        # filtering out taxa without exact matches , saving to db table

        unmatched_taxa = resolved_taxon[resolved_taxon["overall_score"] < .99]

        # writing unmatched taxa to db table taxa_unmatch
        SpecifyDb(db_config_class=picdb_config)
        if len(unmatched_taxa) > 0:
            taxon_unmatch_insert(connection=self.batch_db_connection, logger=self.logger, unmatched_taxa=unmatched_taxa)

        # filtering out taxa with tnrs scores lower than .99 (basically exact match)
        resolved_taxon = resolved_taxon[resolved_taxon["overall_score"] >= .99]

        # dropping uneccessary columns

        resolved_taxon = resolved_taxon.drop(columns=["fullname", "overall_score", "unmatched_terms"])
        # merging columns on full name

        self.record_full = pd.merge(self.record_full, resolved_taxon, on="CatalogNumber", how="left")

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

        self.record_full = self.record_full.drop(columns=['hybrid_base'])

        # executing qualifier separator function
        self.record_full = separate_qualifiers(self.record_full, tax_col='fullname')

        self.record_full['gen_spec'] = self.record_full['gen_spec'].apply(remove_qualifiers)

    def col_clean(self):
        """parses and cleans dataframe columns until ready for upload.
            runs dependent function taxon concat
        """
        self.record_full['verbatim_date'] = self.record_full['verbatim_date'].apply(replace_apostrophes)
        self.record_full['locality'] = self.record_full['locality'].apply(replace_apostrophes)
        date_col_list = ['start_date', 'end_date']
        # changing date formate to Y month day
        for col_string in date_col_list:
            self.record_full[col_string] = pd.to_datetime(self.record_full[col_string],
                                                          format='%m/%d/%Y').dt.strftime('%Y-%m-%d')
        # parsing taxon columns
        self.record_full[['gen_spec', 'fullname',
                          'first_intra',
                          'taxname', 'hybrid_base']] = self.record_full.apply(self.taxon_concat,
                                                                              axis=1, result_type='expand')

        # setting datatypes for columns
        string_list = self.record_full.columns.to_list()

        self.record_full[string_list] = self.record_full[string_list].astype(str)

        # converting hybrid column to true boolean

        self.record_full['Hybrid'] = self.record_full['Hybrid'].apply(str_to_bool)

        self.record_full = self.record_full.replace(['', None, 'nan', np.nan], pd.NA)

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
        """checks if image name/barcode already in attachments table"""
        self.record_full['image_present'] = None
        for index, row in self.record_full.iterrows():
            file_name = os.path.basename(row['image_path'])
            file_name = file_name.lower()
            # file_name = file_name.rsplit(".", 1)[0]
            sql = f'''select origFilename from attachment
                      where origFilename = "{file_name}";'''
            db_name = self.specify_db_connection.get_one_record(sql)
            if db_name is None:
                self.record_full.loc[index, 'image_present'] = False
            else:
                self.record_full.loc[index, 'image_present'] = True

    def check_barcode_match(self):
        """checks if filepath barcode matches catalog number barcode
            just in case merge between folder and specimen level data was not clean"""
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
        """write_upload_csv: writes a copy of csv to PIC upload
            allows for manual review before uploading.
        """
        file_path = f"PIC_upload/PIC_record_{self.date_use}.csv"

        self.record_full.to_csv(file_path, index=False)

        print(f'DataFrame has been saved to csv as: {file_path}')

    def run_all(self):
        """run_all: runs all methods in the class in order"""
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
        # running taxa through TNRS
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

# def full_run():
#     """testing function to run just the first piece o
#           f the upload process"""
#     CsvCreatePicturae(date_string="2023-06-28")
#
# full_run()
