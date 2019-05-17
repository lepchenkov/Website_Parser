from db_connect import Postgres_db
from parse import Parser


class Downloader():

    def __init__(self, db_config, create_new_tables=False):
        self._db = Postgres_db(db_config)
        self._parser = Parser()
        if create_new_tables is True:
            self._db.create_tables()

    def parse_categories(self):
        categories = self._parser.get_categories()
        for category in categories:
            self._db.category_item_insert(category)
        return True
