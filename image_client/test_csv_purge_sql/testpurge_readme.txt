summary: these sql scripts are for general scorched earth purges of records created by test runs of any import script,
        this is NEVER to be used on a real working database or image server. For a more precise purger, see
        image_client/csv_purger.py.

files:
    image_server_purge.sql: removes all image attachments added to image server after selected time window.

    picturae_purge_script.sql: iteratively removes records from casbotany database tables, includes node removal commands
                               to remove unwanted test taxa from the taxon tree.

example-use: You have a testing database and image server on your local machine, you want to do a test upload of data.
             You know the working test copy of your database is a backup from one month prior to the current date,
             after each test you can wipe all records added within the last month/ or day etc. in order to
             return your database to its prior state.