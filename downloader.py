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

    def parse_product_url_from_subcats_lvl2(self, number_of_subcats=10):
        for i in range(number_of_subcats):
            try:
                entry_dict = self._db.get_unparsed_subcat_lvl2_entry()

                product_dicts = self._parser.\
                                get_product_urls_from_lvl2_url(entry_dict.get('url'),
                                                               entry_dict.get('id'),
                                                               entry_dict.get('name'))
                for product_dict in product_dicts:
                    self._db.product_initial_insert(product_dict)
                self._db.update_lvl2_entry_set_parsed_at(entry_id)
            except:
                pass
        return True

    def parse_products_parameters(self, number_of_products_to_parse=20):
        for i in range(number_of_products_to_parse):
            entry_dict = self._db.get_unparsed_product_entry()
            entry_id = entry_dict.get('id')
            entry_url = entry_dict.get('url')
            product_dict, response_code = self._parser\
                                          .get_product_parameters(entry_url)
            if response_code == 200:
                self._db.product_update(entry_id, product_dict)
                feature_dict = product_dict.get('characteristics')
                for feature in feature_dict:
                    feature_value = feature_dict.get(feature, '')
                    self._db.product_features_insert(feature, feature_value,
                                                     entry_id)
            elif response_code == 400:
                self._db.product_update_404(entry_id)
            else:
                self._db.product_update_uknown_error(entry_id)
            return entry_id

    def parse_main_catalog_page_single_run(self):
        for category in self._parser.get_categories():
            category_id = self._db.category_item_insert(category)
            for lvl1_name, lvl1_parent in self._parser.get_lvl1_subcategories():
                if lvl1_parent == category:
                    lvl1_id = self._db.subcat_lvl1_insert(lvl1_name,
                                                                  category_id)
                    for lvl2_dict in self._parser.get_lvl2_subcategories():
                        if lvl2_dict.get('parent') == lvl1_name:
                            self._db.subcat_lvl2_insert(lvl2_dict, lvl1_id)
        return True

    def check_if_stage1_parsing_is_complete(self):
        return self._db.check_if_subcats_lvl2_table_is_not_empty()

    def check_if_stage2_parsing_is_complete(self):
        return self._db.check_if_all_lvl2_links_are_parsed()

    def check_if_stage3_parsing_is_complete(self):
        return self._db.check_if_all_product_links_are_parsed()
