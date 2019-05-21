from downloader import Downloader


db_config = 'postgresql://postgres:test1234@localhost:5432/oma_catalog_test'
dwnld = Downloader(db_config, create_new_tables=True)
dwnld.parse_main_catalog_page_single_run()
