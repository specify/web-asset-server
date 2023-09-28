import sqlite3

class SqlLiteTools:

    def __init__(self):
        pass

    def sql_lite_connection(self, db_name):
        """sql_lite_connection: creates the connection for sqllite db,
            used as the "connection" parameter in other functions
            args:
                db_name: db_name is the file path to the sqlite db."""
        connection = sqlite3.connect(db_name)
        return connection

    def create_insert_statement(self, col_list: list, val_list: list, tab_name: str):
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


    def insert_table_record(self, sql, connection, logger_int):
        """sql_lite_insert: facsimile to insert_table_record in sql_csv_utils.py
            args:
                sql: sql string to send to database
                connection: the sqlite connection used to insert data
                logger_int: the instance of logger to use for error reporting
        """
        connection = sqlite3.connect(database=connection)
        curs = connection.cursor()
        try:
            curs.execute(sql)
        except Exception as e:
            logger_int.error(f"Exception thrown while processing sql: {sql}\n{e}\n")
        try:
            connection.commit()

        except Exception as e:
            raise ValueError(f"sql debug: {e}")

        curs.close()
        connection.close()


    def get_one_match(self, connection, id_col, tab_name, key_col, match, match_type="string"):
        """modified get one record function for sql lite

           args:
                tab_name: the name of the table to select
                id_col: the name of the column in which the unique id is stored
                key_col: column on which to match values
                match: value with which to match key_col
                match_type: "string" or "integer", optional with default as "string"
                            puts quotes around sql terms or not depending on data type """

        sql = ""
        if match_type == "string":
            sql = f'''SELECT {id_col} FROM {tab_name} WHERE `{key_col}` = "{match}";'''
        elif match_type == "integer":
            sql = f'''SELECT {id_col} FROM {tab_name} WHERE `{key_col}` = {match};'''

        connection = sqlite3.connect(database=connection)
        curs = connection.cursor()
        # running sql query
        curs.execute(sql)
        record = curs.fetchone()
        # closing connection
        curs.close()
        connection.close()
        if record is not None:
            return record[0]
        else:
            return record
