from downloader import Downloader


db_config = 'postgresql://postgres:test1234@localhost:5432/oma_catalog_test'
dwnld = Downloader(db_config, create_new_tables=False)
dwnld.parse_products_parameters(number_of_products_to_parse=20)
