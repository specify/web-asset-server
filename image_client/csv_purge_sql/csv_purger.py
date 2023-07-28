from image_client.sql_csv_utils import CsvDatabase
import pandas as pd


CsvDatabase = CsvDatabase()
def casbotany_csv_purger(self, number: int):
    time_stamp_csv = pd.read_csv('upload_time_stamps.csv')

    selected_row = time_stamp_csv[time_stamp_csv['UploadCode' == self.number]]

    time_stamp_list = []

    time_stamp_list.append(selected_row['StartTime'])
    time_stamp_list.append(selected_row['EndTime'])

    table_list = ['collectionobjectattachement', 'attachment',
                  'determination', 'collectionobject', 'collector',
                  'collectingevent', 'locality', 'agent']

    for table in table_list:
        CsvDatabase.sql_time_purger(database='casbotany', table=table,
                                    timestamp1=time_stamp_list[0],
                                    timestamp2=time_stamp_list[1])

        CsvDatabase.sql_time_purger(database='images', table='images',
                                    timestamp1=time_stamp_list[0],
                                    timestamp2=time_stamp_list[1])