import pandas as pd
from importer import Importer
import traceback
import picturae_config

# static methods
def create_name_sql(first_name: str, last_name: str, middle_initial: str, title: str):
    """create_name_sql: create a custom sql string, based on number of non-na arguments, the
                        casbotany database does not recognize empty strings '' and NA as equivalent.
                        Has conditional to ensure the first statement always starts with WHERE
    """
    sql = f'''SELECT AgentID FROM agent'''
    statement_count = 0
    if not pd.isna(first_name):
        statement_count += 1
        sql += f''' WHERE FirstName = "{first_name}"'''
    else:
        statement_count += 1
        sql += f''' WHERE FirstName IS NULL'''

    if not pd.isna(last_name):
        sql += f''' AND LastName = "{last_name}"'''

    else:
        sql += f''' AND FirstName IS NULL'''

    if not pd.isna(middle_initial):
        sql += f''' AND MiddleInitial = "{middle_initial}"'''
    else:
        sql += f''' AND MiddleInitial IS NULL'''

    if not pd.isna(title):
        sql += f''' AND Title = "{title}"'''
    else:
        sql += f''' AND Title IS NULL'''

    sql += ''';'''

    return sql


def create_sql_string(col_list, val_list, tab_name):
    """create_sql_string:
           creates a new sql insert statement given a list of db columns,
           and values to input.
        args:
            col_list: list of database table columns to fill
            val_list: list of values to input into each table
            tab_name: name of the table you wish to insert data into
    """
    # removing brackets, making sure comma is not inside of quotations
    column_list = ', '.join(col_list)
    value_list = ', '.join(f"'{value}'" if isinstance(value, str) else repr(value) for value in val_list)

    sql = f'''INSERT INTO {tab_name} ({column_list}) VALUES({value_list});'''

    return sql

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
        self.logger.debug(sql)
        try:
            cursor.execute(sql)
        except Exception as e:
            print(f"Exception thrown while processing sql: {sql}\n{e}\n", flush=True)
            self.logger.error(traceback.format_exc())

        self.specify_db_connection.commit()

        cursor.close()


