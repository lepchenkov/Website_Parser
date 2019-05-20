from db_connect import Postgres_db
from parse import Parser


class Downloader():

    def __init__(self, db_config, create_new_tables=False):
        self._db = Postgres_db(db_config)
        self._parser = Parser()
        if create_new_tables is True:
            try:
                self._db.drop_existing_tables_from_db()
            except:
                pass
            self._db.create_tables()

    def parse_categories(self):
        for category in self._parser.get_categories():
            self._db.category_item_insert(category)
        return True

    def parse_lvl1_subcategories(self):
        for name, parent in self._parser.get_lvl1_subcategories():
            self._db.subcat_lvl1_insert(name, parent)
        return True

    def parse_lvl2_subcategories(self):
        for subcat_lvl2_dict in self._parser.get_lvl2_subcategories():
            self._db.subcat_lvl2_insert(subcat_lvl2_dict)
        return True

    def parse_products_initial(self):
        i = 0
        for product_dict in self._parser.get_product_link():
            self._db.product_initial_insert(product_dict)
            i += 1
            if i == 200:
                break
        return True

    def parse_products_parameters(self):
        self._db.product_update()
        self._db.product_featurex_insert()
        pass
