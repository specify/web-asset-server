summary: the purpose of these files to upload csv and image records of newly digitized specimens by Picturae.


setup:
      1. create a picturae_config.py file with the correct database settings and folder setting for your environment.
      2. install all packages from the requirements.txt file
      2. run the picturae_DDL to create the required error tracking tables in the database
      3. (optional) install R to enable r2py package to work properly
      4. in order to run picturae_importer from the command line run with example date 2023-06-28:
         'python image_client/client_tools.py Botany_PIC import 2023-06-28'

        if no date argument picturae_import will use the image/ csv folder name with the latest date.


file list:
    Python files:

    picturae_csv_create.py: This .py file takes csv files stored in wrangles the columns into a format
                            which is clean enough for upload to the database. This file also is dependent on
                            the R_TNRS file in /taxon_check to check validity and spelling of taxonomic nomenclature.

    picturae_importer.py: This .py file takes the prepared csv file from picturae_csv_create and uploads parsed data
                          to database tables to create a collection object record. This file is called from
                          client_tools.py , and in turn calls picturae_csv_create.py and botany_importer.py

    picturae_DDL: (run this before running the importer!)
                    This DDL creates new sql tables for troubleshooting problems with taxa and batch uploads:

                          taxa_unmatch : taxa which did not pass TNRS successfully
                          picturaetaxa_added: new taxa added to the database
                          And creates and upload log:
                          picturae_batch: tracks each upload with timestamps and MD5 code,
                                           can be used for purging or troubleshooting.

    data_utils: .py file which contains functions import for parsing lists, strings and datetime

    sql_csv_utils: .py file which contains functions used to quickly parse sql statements for insert/update/select

    csv_purger: .py file used to do a controlled purge using md5 and timestamps of upload batches from picturae_import

    picturae_config.template.py: template for database credentials, and for specifying image and csv folder locations.
                                 contains a date_str variable that can be changed in the command line (default behavior



    R files:
        R_TNRS: a taxonomic name resolver in the taxon_check/ folder. Further details in .readme.txt
                in the taxon_check/ folder

    SQL files:
        in test_csv_purge_sq/:
        !! warning : only use these on a testing database, quick scorched earth method of purging test records.
        image_server_purge.sql: scorched earth purge of images added to DB in a custom time frame
        picturae_purge_script.sql: scorched earth purge of records added to DB in a custom time frame