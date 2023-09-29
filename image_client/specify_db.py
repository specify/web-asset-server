from db_utils import DbUtils
import logging
class SpecifyDb(DbUtils):
    def __init__(self, db_config_class):

        self.specify_db_connection = super().__init__(
            db_config_class.USER,
            db_config_class.PASSWORD,
            db_config_class.SPECIFY_DATABASE_PORT,
            db_config_class.SPECIFY_DATABASE_HOST,
            db_config_class.SPECIFY_DATABASE)
