"""This file is home to the DatabasePurger, used with specific MD5 codes to purge upload batches to the
    database.
    NOTE: only use this process if your upload process includes a LOCK user command
          to prevent other changes to the database during upload"""
import picturae_config
from importer import Importer
import traceback

# def parse_command_undo():
#     """parse_command_undo: parses arguments from command line for purging picturae upload batches.
#                           Allowing user to pass md5 codes as arguments to the PicturaeUndoBatch class
#                           from the command line."""
#     parser = argparse.ArgumentParser(
#              description=f"""
#                  Tool to manipulate images on the CAS image server.
#
#                  Available collections: Botany
#
#                  Commands: import, search, purge. Collection is mandatory.
#                  """,
#              formatter_class=argparse.RawTextHelpFormatter, add_help=True)
#
#     parser.add_argument('--m', '-md5', nargs="?", help='md5 batch to remove from database', default=None)
#
#     return parser.parse_args()



class PicturaeUndoBatch(Importer):
    def __init__(self, MD5):
        super().__init__(picturae_config, "Botany")
        self.purge_code = MD5
        self.run_all(MD5=self.purge_code)

    def batch_undo_timestamps(self, database, table, timestamp1, timestamp2):
        """sql_time_purger: purges records from select database added between two timestamps.
                args:
                    database: name of the database which you want to use.
                    table: name of the table which you want to purge records from.
                    timestamp1: the start time/ lower bound of the TimestampCreated you want to purge
                    timestamp2: the end time/ upper bound of the TimestampCreated you want to purge
            """
        try:
            cursor = self.specify_db_connection.get_cursor()
        except Exception as e:
            self.logger.error(f"Connection Error: {e}")

        sql = f'''DELETE FROM {database}.{table} WHERE TimestampCreated >= 
                  "{timestamp1}" AND TimestampCreated <= "{timestamp2}"'''
        self.logger.info(f'running query: {sql}')
        self.logger.debug(sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            self.logger.error(f"Exception thrown while processing sql: {sql}\n{e}\n", flush=True)
            self.logger.error(traceback.format_exc())

        self.specify_db_connection.commit()

        cursor.close()

    def batch_tree_pruner(self, database, table, timestamp1, timestamp2):
        """sql_tree_purger: used to iteratively remove taxa created by a batch upload.
                            creates a temporary table and removes taxa on the taxa tree
                            added between two timestamps
                            from the bottom up until no nodes are left.
            args:
                database: the name of the database which will be used.
                table: the name of the taxon tree table from which records will be removed
                timestamp1: the start time/ lower bound of the TimestampCreated you want to purge
                timestamp2: the end time/ upper bound of the TimestampCreated you want to purge
        """

        try:
            cursor = self.specify_db_connection.get_cursor()
        except Exception as e:
            self.logger.error(f"Connection Error: {e}")
        sql_temp = f'''CREATE TEMPORARY TABLE temp_leaf_nodes AS SELECT TaxonID FROM {database}.{table} WHERE TaxonID
                       NOT IN (SELECT DISTINCT ParentID FROM {database}.{table}
                       WHERE ParentID IS NOT NULL) 
                       AND TimestampCreated >= "{timestamp1}" AND TimestampCreated <= "{timestamp2}";'''

        sql_del = f'''DELETE FROM {database}.{table} WHERE TaxonID IN (SELECT TaxonID FROM temp_leaf_nodes);'''

        sql_drop = f'''DROP TEMPORARY TABLE IF EXISTS temp_leaf_nodes;'''
        rows_affected = 0
        while True:
            try:
                cursor.execute(sql_temp)
                cursor.execute(sql_del)
                rows_affected = cursor.rowcount
                cursor.execute(sql_drop)
            except Exception as e:
                print(f"Exception thrown while processing sql: \n{e}\n", flush=True)
                self.logger.error(traceback.format_exc())

            if rows_affected == 0:
                break
        self.specify_db_connection.commit()

        cursor.close()

    # def batch_log_clear(self, MD5: str):



    def picturae_csv_undo(self, database: str, table: str, MD5: str):
        """casbotany_csv_purger: runs sql commands to database, to purge sql records created between two timestamps
                                 in which the original upload script was run,
            uses log of sql uploads to retrieve records organized by generated MD5 code.
            args:
                database:name of database to use
                table: the name of the table on which upload timestamps and MD5s are stored.
                MD5: the verbatim md5 string format of the desired upload to purge.

        """
        md5_start = f'''SELECT StartTimeStamp FROM {database}.{table} WHERE batch_MD5 = "{MD5}";'''

        start_time = self.specify_db_connection.get_one_record(md5_start)

        md5_end = f'''SELECT EndTimeStamp FROM {database}.{table} WHERE batch_MD5 = "{MD5}";'''

        end_time = self.specify_db_connection.get_one_record(md5_end)

        if start_time is None or end_time is None:
            raise ValueError(f"{MD5} not found in database table")

        time_stamp_list = []

        time_stamp_list.append(str(start_time))
        time_stamp_list.append(str(end_time))

        table_list = ['collectionobjectattachment', 'attachment',
                      'determination', 'collectionobject', 'collector',
                      'collectingevent', 'locality', 'agent']

        for table in table_list:
            self.batch_undo_timestamps(database='casbotany', table=table,
                                       timestamp1=time_stamp_list[0],
                                       timestamp2=time_stamp_list[1])

        table = "taxon"

        self.batch_tree_pruner(database='casbotany', table=table,
                               timestamp1=time_stamp_list[0],
                               timestamp2=time_stamp_list[1])


    def run_all(self, MD5):
        print("runnning PIC_undo_batch")
        self.picturae_csv_undo(database="casbotany", table="picturae_batch", MD5=MD5)


# def run_picturae_class(MD5: str):
#     if MD5 is None:
#         raise ValueError("No md5 code given, exiting program.")
#     else:
#         picturae_int = PicturaeUndoBatch(MD5=MD5)
#
#         picturae_int.run_all()
#
#         print(f"upload batch with code {MD5} removed from database")
#
#
# if __name__ == '__main__':
#
#     args = parse_command_undo()
#     # parsing md5 code from the command line
#     md5_parse = str(args.md5)
#
#     run_picturae_class(MD5=md5_parse)
