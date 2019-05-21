from downloader import Downloader


db_config = 'postgresql://postgres:test1234@localhost:5432/oma_catalog_test'
dwnld = Downloader(db_config, create_new_tables=False)
dwnld.parse_product_url_from_subcats_lvl2(number_of_subcats=10)
