from downloader import Downloader
import time


db_config = 'postgresql://postgres:test1234@localhost:5432/oma_catalog_test'


def check_if_stage1_is_not_complete():
    pass


def check_if_stage2_is_not_complete():
    pass


def check_if_stage3_is_not_complete():
    pass


if __name__ == __main__:
    while check_if_stage1_is_not_complete():
        dwnld = Downloader(db_config, create_new_tables=True)
        dwnld.parse_main_catalog_page_single_run()
    while check_if_stage2_is_not_complete():
        try:
            dwnld = Downloader(db_config, create_new_tables=False)
            dwnld.parse_product_url_from_subcats_lvl2(number_of_subcats=10)
            time.sleep(10)
        except:
            pass
    while check_if_stage3_is_not_complete():
        try:
            dwnld = Downloader(db_config, create_new_tables=False)
            dwnld.parse_products_parameters(number_of_products_to_parse=20)
            time.sleep(10)
        except:
            pass
