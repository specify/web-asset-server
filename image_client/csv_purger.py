import picturae_config as picturae_config
from importer import Importer
import traceback
import pandas as pd


class CsvDatabase(Importer):
    def __init__(self):
        super().__init__(picturae_config, "Botany")

    def sql_time_purger(self, database, table, timestamp1, timestamp2):
        try:
            cursor = self.specify_db_connection.get_cursor()
        except Exception as e:
            self.logger.error(f"Connection Error: {e}")

        sql = f'''DELETE FROM {database}.{table} WHERE TimestampCreated > 
                  "{timestamp1}" AND TimestampCreated < "{timestamp2}"'''
        self.logger.info(f'running query: {sql}')
        print(sql)
        self.logger.debug(sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f"Exception thrown while processing sql: {sql}\n{e}\n", flush=True)
            self.logger.error(traceback.format_exc())

        self.specify_db_connection.commit()

        cursor.close()


CsvDatabase = CsvDatabase()
def casbotany_csv_purger(number: int):
    time_stamp_csv = pd.read_csv('csv_purge_sql/upload_time_stamps.csv')

    selected_row = time_stamp_csv[time_stamp_csv['UploadCode'] == number]

    time_stamp_list = []

    time_stamp_list.append(selected_row['StartTime'].to_string(index=False))
    time_stamp_list.append(selected_row['EndTime'].to_string(index=False))


    table_list = ['collectionobjectattachment', 'attachment',
                  'determination', 'collectionobject', 'collector',
                  'collectingevent', 'locality', 'agent']

    for table in table_list:
        CsvDatabase.sql_time_purger(database='casbotany', table=table,
                                    timestamp1=time_stamp_list[0],
                                    timestamp2=time_stamp_list[1])


casbotany_csv_purger(number=476987)





# class_int = CsvDatabase()
#
# class_int.sql_time_purger("casbotany", "collectionobjectattachment",
#                           "2023-07-28 09:28:13.238155", "2023-07-28 09:28:45.936700")
