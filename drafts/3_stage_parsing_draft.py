from downloader import Downloader


db_config = 'postgresql://postgres:test1234@localhost:5432/oma_catalog_test'
dwnld = Downloader(db_config, create_new_tables=True)
dwnld.parse_main_catalog_page_single_run()


db_config = 'postgresql://postgres:test1234@localhost:5432/oma_catalog_test'
dwnld = Downloader(db_config, create_new_tables=False)
dwnld.parse_product_url_from_subcats_lvl2(number_of_subcats=10)


db_config = 'postgresql://postgres:test1234@localhost:5432/oma_catalog_test'
dwnld = Downloader(db_config, create_new_tables=False)
dwnld.parse_products_parameters(number_of_products_to_parse=20)
