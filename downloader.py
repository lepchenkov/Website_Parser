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

    def parse_product_url_from_subcats_lvl2(self,number_of_subcats=10):
        for i in range(number_of_subcats):
            entry = self._db.get_unparsed_subcat_lvl2_entry()
            entry_id = entry[0]
            entry_url = entry[1]
            entry_name = entry[2]
            product_dicts = self._parser.\
                            get_product_urls_from_subcatery_lvl2_url(entry_url,
                                                                     entry_id,
                                                                     entry_name)
            for product_dict in product_dicts:
                self._db.product_initial_insert(product_dict)
            self._db.update_lvl2_entry_set_parsed_at(entry_id)
        return True

    def parse_products_parameters(self, number_of_products_to_parse=20):
        for i in range(number_of_products_to_parse):
            entry = self._db.get_unparsed_product_entry()
            entry_id = entry[0]
            entry_url = entry[1]
            product_dict = self._parser.get_product_parameters(entry_url)
            self._db.product_update(entry_id, product_dict)
            feature_dict = product_dict.get('characteristics')
            for feature in feature_dict:
                feature_value = feature_dict.get(feature, '')
                self._db.product_features_insert(feature, feature_value,
                                                 entry_id)
        return True
