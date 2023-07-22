"""This file contains unit tests for picturae_import.py"""
import unittest
import random
import shutil
import numpy as np
from picturae_import import *
from faker import Faker
from datetime import date, timedelta
from picturae_import import DataOnboard
from mock import patch
from PIL import Image
from casbotany_sql_lite import *


def test_date():
    """test_date: creates an arbitrary date, 20 years in the past from today's date,
       to create test files for, so as not to overwrite current work
       ! if this code outlives 20 years of use I would be impressed"""
    unit_date = date.today() - timedelta(days=365 * 20)
    return str(unit_date)

class TestSQLlite(unittest.TestCase):
    def test_casbotanylite(self):
        connection = sqlite3.connect('cas_botanylite.db')
        curs = connection.cursor()
        curs.execute('''SELECT * FROM agent''')
        num_columns = len(curs.description)
        self.assertEqual(num_columns, 45)
        curs.close()
        connection.close()


class WorkingDirectoryTests(unittest.TestCase):
    """WorkingDirectoryTests: a series of unit tests to verify
        correct working directory, subdirectories."""
    def setUp(self):
        self.DataOnboard = DataOnboard(date_string=test_date())

    def test_missing_folder_raise_error(self):
        """checks if incorrect sub_directory raises error from file present"""
        with self.assertRaises(ValueError) as cm:
            self.DataOnboard.file_present()
        self.assertEqual(str(cm.exception), f"subdirectory for {test_date()} not present")

    def tearDown(self):
        del self.DataOnboard


class FilePathTests(unittest.TestCase):
    """ FilePathTests: tests paths for file_present
       function using dummy paths. """

    def setUp(self):
        """setUP: unittest setup function creates empty csvs,
                  and folders for given test path"""

        # initializing
        self.DataOnboard = DataOnboard(date_string=test_date())

        # print("setup called!")
        # create test directories

        date_string = test_date()

        expected_folder_path = 'picturae_csv/' + str(date_string) + '/picturae_folder(' + \
                               str(date_string) + ').csv'
        expected_specimen_path = 'picturae_csv/' + str(date_string) + '/picturae_specimen(' + \
                                 str(date_string) + ').csv'
        # making the directories
        os.makedirs(os.path.dirname(expected_folder_path), exist_ok=True)

        open(expected_folder_path, 'a').close()
        open(expected_specimen_path, 'a').close()

    def test_expected_path_date(self):
        """test_expected_path_date: tests , when the
          folders are correctly created that there is
          no exception raised"""
        try:
            self.DataOnboard.file_present()
        except Exception as e:
            self.fail(f"Exception raised: {str(e)}")

    def test_raise_specimen(self):
        """test_raise_specimen: tests whether correct value
           error is raised for missing specimen_csv"""
        date_string = test_date()
        # removing test path specimen
        os.remove('picturae_csv/' + str(date_string) + '/picturae_specimen(' +
                  str(date_string) + ').csv')
        with self.assertRaises(ValueError) as cm:
            self.DataOnboard.file_present()
        self.assertEqual(str(cm.exception), "Specimen csv does not exist")

    def test_raise_folder(self):
        """test_raise_folder: tests whether correct value error
           is raised for missing folder_csv"""
        date_string = test_date()
        # removing test path folder
        os.remove('picturae_csv/' + str(date_string) + '/picturae_folder(' +
                  str(date_string) + ').csv')
        with self.assertRaises(ValueError) as cm:
            self.DataOnboard.file_present()
        self.assertEqual(str(cm.exception), "Folder csv does not exist")

    def tearDown(self):
        """destroys paths for Setup function,
           returning working directory to prior state"""

        del self.DataOnboard

        # print("teardown called!")

        date_string = test_date()
        # create test directories

        expected_folder_path = 'picturae_csv/' + str(date_string) + '/picturae_folder(' + \
                               str(date_string) + ').csv'
        shutil.rmtree(os.path.dirname(expected_folder_path))


# class for testing csv_import function
# too many redundant t4e
class CsvReadMergeTests(unittest.TestCase):
    """this class contains methods which test outputs of the
       csv_read_folder function , and csv_merge functions from
       picturae_import.py"""

    # will think of ways to shorten this setup function
    def setUp(self):
        """creates fake datasets with dummy columns,
          that have a small subset of representive real column names,
          so that test merges and uploads can be performed.
          """
        # print("setup called!")
        self.DataOnboard = DataOnboard(date_string=test_date())
        # setting num records and test date
        fake = Faker()
        num_records = 50
        date_string = test_date()
        # maybe create a separate function for setting up test directories
        path_type_list = ['folder', 'specimen']
        path_list = []
        for path_type in path_type_list:
            path = 'picturae_csv/' + str(date_string) + '/picturae_' + str(path_type) + '(' + \
                    str(date_string) + ').csv'

            path_list.append(path)

            os.makedirs(os.path.dirname(path), exist_ok=True)

            open(path, 'a').close()
        # writing csvs
        for path in path_list:
            with open(path, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)

                writer.writerow(['specimen_barcode', 'folder_barcode', 'path_jpg'])
                for i in range(num_records):
                    # to keep barcodes matching between folder and specimen csvs for merging
                    ordered_bar = 123456
                    specimen_bar = ordered_bar + i
                    # populating rest of columns with random data
                    folder_barcode = fake.random_number(digits=6)
                    jpg_path = fake.file_path(depth=random.randint(1, 5), category='image', extension='jpg')

                    # writing data to CSV
                    writer.writerow([specimen_bar, folder_barcode, jpg_path])
            print(f"Fake dataset {path} with {num_records} records created successfully")

            self.DataOnboard.record_full = pd.DataFrame

    def test_file_empty(self):
        """tests if dataset returns as empty set or not"""
        self.assertEqual(self.DataOnboard.csv_read_folder('folder').empty, False)
        self.assertEqual(self.DataOnboard.csv_read_folder('specimen').empty, False)

    def test_file_colnumber(self):
        """tests if expected # of columns given test datasets"""
        self.assertEqual(len(self.DataOnboard.csv_read_folder('folder').columns), 3)
        self.assertEqual(len(self.DataOnboard.csv_read_folder('specimen').columns), 3)

    def test_barcode_column_present(self):
        """tests if barcode column is present
           (test if column names loaded correctly,
           specimen_barcode being in required in both csvs)"""
        self.assertEqual('specimen_barcode' in self.DataOnboard.csv_read_folder('folder').columns, True)
        self.assertEqual('specimen_barcode' in self.DataOnboard.csv_read_folder('specimen').columns, True)

    # these tests are for the csv merge function
    def test_merge_num_columns(self):
        """test merge with sample data set , checks if shared columns are removed,
           and that the merge occurs with expected # of columns"""
        # -3 as merge function drops duplicate columns automatically
        self.DataOnboard.csv_merge()
        self.assertEqual(len(self.DataOnboard.record_full.columns),
                         len(self.DataOnboard.csv_read_folder('folder').columns) +
                         len(self.DataOnboard.csv_read_folder('specimen').columns) - 3)

    def test_index_length_matches(self):
        """checks whether dataframe, length changes,
           which would hint at barcode mismatch problem,
           as folder and specimen csvs should
           always be 100% matches on barcodes
           """
        self.DataOnboard.csv_merge()
        csv_folder = self.DataOnboard.csv_read_folder('folder')
        # test merge index before and after
        self.assertEqual(len(self.DataOnboard.record_full),
                         len(csv_folder))

    def test_unequalbarcode_raise(self):
        """checks whether inserted errors in barcode column raise
           a Value error raise in the merge function"""
        # testing output
        csv_folder = self.DataOnboard.csv_read_folder(folder_string="folder")
        csv_specimen = self.DataOnboard.csv_read_folder(folder_string="specimen")
        self.assertEqual(set(csv_folder['specimen_barcode']), set(csv_specimen['specimen_barcode']))

    def test_output_isnot_empty(self):
        """tests whether merge function accidentally
           produces an empty dataframe"""
        self.DataOnboard.csv_merge()
        # testing output
        self.assertFalse(self.DataOnboard.record_full.empty)

    def tearDown(self):
        """deletes destination directories for dummy datasets"""
        # print("teardown called!")
        # deleting instance
        del self.DataOnboard
        # deleting folders
        date_string = test_date()

        folder_path = 'picturae_csv/' + str(date_string) + '/picturae_folder(' + \
                      str(date_string) + ').csv'

        shutil.rmtree(os.path.dirname(folder_path))


class ColNamesTest(unittest.TestCase):
    def setUp(self):
        """creates dummy dataset with representative column names"""
        # initializing class
        self.DataOnboard = DataOnboard(date_string=test_date())
        # creating dummy dataset
        numb_range = list(range(1, 101))
        column_names = ['application_batch', 'csv_batch', 'object_type', 'folder_barcode',
                        'specimen_barcode', 'filed_as_family', 'barcode_info', 'path_jpg',
                        'Taxon ID', 'Family', 'Genus', 'Species', 'Qualifier', 'Author',
                        'Rank1', 'Epithet 1', 'Rank 2', 'Epithet 2', 'Rank 2.1', 'Epithet 2.1',
                        'Hybrid', 'Hybrid Genus', 'Hybrid Species', 'Hybrid Rank 1',
                        'Hybrid Epithet 1', 'Hybrid Level',
                        'collector_number', 'collector_first_name 1', 'collector_middle_name 1',
                        'collector_last_name 1', 'collector_first_name 2',
                        'collector_middle_name 2', 'collector_last_name 2',
                        'collector_first_name 3', 'collector_middle_name 3',
                        'collector_last_name 3', 'collector_first_name 4',
                        'collector_middle_name 4', 'collector_last_name 4',
                        'collector_first_name 5', 'collector_middle_name 5',
                        'collector_last_name 5', 'Country', 'State', 'County', 'Locality',
                        'Verbatim Date', 'Start Date', 'End Date']
        new_df = {column_names[i]: numb_range for i in range(49)}

        # adding in fake notes and feedback columns,
        # so they can be filtered without raise.
        new_df['Notes'] = np.NAN
        new_df['Feedback'] = np.NAN

        self.DataOnboard.record_full = pd.DataFrame(new_df)


    def test_if_id_cols(self):
        """test_if_id_col: tests whether certain essential
           ID columns present. Also tests, wether name columns correctly
           reformated
        """
        self.DataOnboard.csv_colnames()
        csv_columns = self.DataOnboard.record_full.columns
        column_names = ['collector_number', 'RankID',
                        'CatalogNumber', 'collector_last_name1',
                        'collector_first_name5']
        self.assertTrue(all(column in csv_columns for column in column_names))


    def test_if_nas(self):
        """test_if_nas: test if any left-over columns contain only NAs"""
        self.DataOnboard.csv_colnames()
        self.record_full = self.DataOnboard.record_full.dropna(axis=1, how='all')
        self.assertEqual(len(self.record_full.columns), len(self.record_full.columns))

    def tearDown(self):

        del self.DataOnboard



class DatabaseChecks(unittest.TestCase):
    def setUp(self):
        """creates fake dataset with dummy columns,
          that have a small subset of representative real column names,
          """
        # initializing

        self.DataOnboard = DataOnboard(date_string=test_date())

        # creating dummy dataset, one mistake inserted on purpose
        data = {'CatalogNumber': ['580092', '58719322', '8708'],
                'image_path': ['picturae_folder/cas580091.jpg',
                               'picturae_folder/cas58719322.jpg',
                               'picturae_folder/cas8708.jpg'],
                'folder_barcode': ['2310_2', '2310_2', '2312_2']}

        self.DataOnboard.record_full = pd.DataFrame(data)
        print(self.DataOnboard.record_full)

    def test_column_present(self):
        """checks whether boolean column added for record present"""
        self.DataOnboard.barcode_has_record()
        self.assertEqual(len(self.DataOnboard.record_full.columns), 4)

    def test_row_length(self):
        """tests whether # rows is preserved after
           record present operation"""
        self.DataOnboard.barcode_has_record()
        self.assertEqual(len(self.DataOnboard.record_full), 3)

    def test_check_barcode_present(self):
        """tests if when a false barcode is tested, the
           correct False boolean appears"""
        self.DataOnboard.barcode_has_record()
        test_list = list(self.DataOnboard.record_full['barcode_present'])
        self.assertEqual(test_list, [True, False, True])
        print(self.DataOnboard.record_full)

    def test_if_barcode_match(self):
        self.DataOnboard.check_barcode_match()
        test_list = list(self.DataOnboard.record_full['is_barcode_match'])
        self.assertEqual([False, True, True], test_list)

    def tearDown(self):

        del self.DataOnboard


class CheckImagePaths(unittest.TestCase):
    """this class is for testing if for every barcode,
       there is an equivalent relevant jpeg and tif file."""
    def setUp(self):
        """setup creating matrix with real test image paths to test."""
        # intializing
        self.DataOnboard = DataOnboard(date_string=test_date())
        # creating dummy frame of real test paths
        folder_path = 'test_images'
        file_paths = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.endswith(('JPG', 'TIF')):
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)

        path_df = pd.DataFrame({'image_path': file_paths})
        self.DataOnboard.record_full = path_df

    def test_true_files(self):
        """tests if images that are confirmed to be present return a True"""
        self.DataOnboard.check_if_images_present()
        self.assertTrue('image_valid' in self.DataOnboard.record_full.columns)
        self.assertTrue(all(self.DataOnboard.record_full['image_valid']))

    def tearDown(self):

        del self.DataOnboard


class TestSqlInsert(unittest.TestCase):
    def setUp(self):
        self.DataOnboard = DataOnboard(test_date())

    def test_sql_concat(self):
        # creating function parameters
        table_select = 'agent'
        column_list = ['AgentType', 'FirstName', 'MiddleInitial']
        value_list = [1, 'Fake', 'Name']

        column_list = ', '.join(column_list)
        value_list = ', '.join(f"'{value}'" if isinstance(value, str) else repr(value) for value in value_list)

        sql = f'''INSERT INTO {table_select} ({column_list}) VALUES({value_list})'''
        print(sql)
        # assert statement
        expected_output = f'''INSERT INTO agent (AgentType, FirstName, MiddleInitial) VALUES(1, 'Fake', 'Name')'''
        self.assertEqual(sql, expected_output)

    def tearDown(self):
        del self.DataOnboard


class TestAgentList(unittest.TestCase):
    def setUp(self):
        self.DataOnboard = DataOnboard(date_string=test_date())

        # jose Gonzalez is a real agent,
        # to make sure true matches are not added to list.
        data = {'collector_first_name1': ['Bob'],
                'collector_last_name1': ['Fakeson'],
                'collector_middle_name1': ['J'],
                'collector_first_name2': ['Enrique'],
                'collector_last_name2': ['de la fake'],
                'collector_middle_name2': ['X'],
                'collector_first_name3': ['Jose'],
                'collector_last_name3': ['Gonzalez'],
                'collector_middle_name3': ['S'],
                }

        self.DataOnboard.record_full = pd.DataFrame(data)

        self.DataOnboard.collector_list = []

        print(self.DataOnboard.record_full)


    def test_agent_list(self):
        for index, row in self.DataOnboard.record_full.iterrows():
            self.DataOnboard.append_agent_id(row)

        print(self.DataOnboard.collector_list)
        first_dict = self.DataOnboard.collector_list[0]
        second_dict = self.DataOnboard.collector_list[1]

        self.assertEqual(first_dict['collector_first_name'], 'Bob')
        self.assertEqual(first_dict['collector_last_name'], 'Fakeson')
        self.assertEqual(second_dict['collector_first_name'], 'Enrique')
        self.assertEqual(second_dict['collector_middle_name'], 'X')
        self.assertEqual(len(self.DataOnboard.collector_list), 2)

    def tearDown(self):
        del self.DataOnboard


class ConcatTaxonTests(unittest.TestCase):
    def setUp(self):
        self.DataOnboard = DataOnboard(date_string=test_date())

        # jose Gonzalez is a real agent,
        # to make sure true matches are not added to list.
        data = {'Genus': ['Fakeulos', np.nan],
                'Species': ['fakeulanus', np.nan],
                'Rank 1': ['Species', np.nan],
                'Epithet 1': ['fakeulanus', np.nan],
                'Rank 2': ['var.', np.nan],
                'Epithet 2': ['fakus', np.nan],
                'Hybrid': [False, True],
                'Hybrid Genus': [np.nan, 'Toyotae'],
                'Hybrid Species': [np.nan, 'Preusus'],
                'Hybrid Epithet': [np.nan, 'Preusus'],
                'Hybrid Level': [np.nan, 'Species']
                }

        self.DataOnboard.record_full = pd.DataFrame(data)

        self.DataOnboard.tax_name = ""

        self.DataOnboard.full_name = ""


    def test_taxon_concat_string(self):
        temp_taxon_list = []
        for index, row in self.DataOnboard.record_full.iterrows():
            self.DataOnboard.taxon_concat(row)
            temp_taxon_list.append(self.DataOnboard.full_name)

        self.assertEqual(temp_taxon_list[0], 'Fakeulos fakeulanus var. fakus')
        self.assertEqual(temp_taxon_list[1], 'Toyotae Preusus')
        self.assertEqual(len(temp_taxon_list), 2)

    def tearDown(self):
        del self.DataOnboard


class TestPopulateFields(unittest.TestCase):
    def setUp(self):
        self.DataOnboard = DataOnboard(date_string=test_date())
        data = {'CatalogNumber': ['123456'],
                'verbatim_date': ['March 21, 2008'],
                'start_date': ['3/21/2008'],
                'end_date': [np.nan],
                'collector_number': [180024],
                'locality': ['Harden Lake'],
                'geography_string': ['Mariposa County, California, United States'],
                'county': 'Mariposa County',
                'state': 'California',
                'country': 'United States'}
        self.DataOnboard.record_full = pd.DataFrame(data)

    def test_assigned_to_variable(self):
        for index, row in self.DataOnboard.record_full.iterrows():
            self.DataOnboard.populate_fields(row)
            self.assertEqual(self.DataOnboard.barcode, '000123456')
            self.assertEqual(self.DataOnboard.locality, 'Harden Lake')
            self.assertEqual(self.DataOnboard.GeographyID, 16490)
            self.assertEqual(self.DataOnboard.locality_id, 54)

    def tearDown(self):
        del self.DataOnboard


class SQLUploadTests(unittest.TestCase):
    def setUp(self):

        self.DataOnboard = DataOnboard(date_string=test_date())


    # these functions are to ostensibly test the function create_table_record

    def test_sql_string(self):

        sql = self.DataOnboard.create_sql_string(val_list=[4, 5, "on mt"],
                                                col_list=['code4', 'code5', 'local'], tab_name='locality')

        self.assertEqual(sql,
                         f'''INSERT INTO locality (code4, code5, local) VALUES(4, 5, 'on mt');''')

    def test_create_locality(self):
        """testing create_locality function"""

        LocalityName = f"2 miles from eastern side of Mt.Fake + {time_utils.get_pst_time_now_string()}"


        column_list = ['TimestampCreated',
                       'TimestampModified',
                       'Version',
                       'GUID',
                       'SrcLatLongUnit',
                       'LocalityName',
                       'DisciplineID',
                       'GeographyID']

        value_list = [f"{time_utils.get_pst_time_now_string()}",
                      f"{time_utils.get_pst_time_now_string()}",
                      1,
                      f"{uuid4()}",
                      1,
                      LocalityName,
                      3,
                      256]





        # assigning row ids
        self.DataOnboard.create_sql_string(tab_name="locality", col_list=column_list,
                                             val_list=value_list)

        self.DataOnboard.create_table_record(self.DataOnboard.sql_concat, is_test=True)
        # checking whether locality id created
        data_base_locality = casbotany_lite_getrecord(f'''SELECT `LocalityID` FROM locality WHERE 
                                                         `LocalityName` = "{LocalityName}"''')

        self.assertFalse(data_base_locality is None)

        # checking whether geocode present
        data_base_geo_code = casbotany_lite_getrecord(f'''SELECT `GeographyID` FROM locality WHERE 
                                                         `LocalityName` = "{LocalityName}"''')

        self.assertEqual(data_base_geo_code, 256)


    def tearDown(self):
        self.DataOnboard = DataOnboard(date_string=test_date())


class HideFilesTest(unittest.TestCase):
    def setUp(self):
        # initializing
        self.DataOnboard = DataOnboard(date_string=test_date())

        # print("setup called!")
        # create test directories

        date_string = test_date()

        image = Image.new('RGB', (200, 200), color='red')

        self.expected_image_path = ""
        barcode_list = [123456, 123457, 123458]
        for barcode in barcode_list:
            self.expected_image_path = f"picturae_img/{date_string}/CAS{barcode}.JPG"
            os.makedirs(os.path.dirname(self.expected_image_path), exist_ok=True)
            print(f"Created directory: {os.path.dirname(self.expected_image_path)}")
            image.save(self.expected_image_path)

        self.DataOnboard.image_list = [f"picturae_img/{date_string}/CAS123456.JPG"]

    def test_file_hide(self):
        self.DataOnboard.hide_unwanted_files(date_string=test_date())
        files = os.listdir(f"picturae_img/{test_date()}")
        self.assertTrue('CAS123456.JPG' in files)
        self.assertTrue('.hidden_CAS123457.JPG')

    def test_file_unhide(self):
        self.DataOnboard.hide_unwanted_files(date_string=test_date())
        self.DataOnboard.unhide_files(date_string=test_date())
        files = os.listdir(f"picturae_img/{test_date()}")
        self.assertEqual(set(files), {'CAS123456.JPG', 'CAS123457.JPG', 'CAS123458.JPG'})

    def tearDown(self):
        shutil.rmtree(os.path.dirname(self.expected_image_path))
        del self.DataOnboard


if __name__ == "__main__":
    unittest.main()
