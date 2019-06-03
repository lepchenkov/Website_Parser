#!/usr/bin/env python3
import logging
from downloader import Downloader
from db_configurator import get_config_string


def main():
    logging.basicConfig(filename='oma_parsing.log', level=logging.INFO,
                        format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info('Started')
    db_config = get_config_string()
    download = Downloader(db_config, create_new_tables=False)
    logging.info('Downloader initiated with create_new_tables=False')
    if not download.check_if_stage1_parsing_is_complete():
        logging.info('Stage_1 parsing started')
        download = Downloader(db_config, create_new_tables=True)
        download.parse_main_catalog_page_single_run()
        logging.info('Stage_1 parsing is finished')
    logging.info('Stage_2 parsing started')
    while not download.check_if_stage2_parsing_is_complete():
        download.parse_product_url_from_subcats_lvl2(number_of_subcats=1)
    logging.info('Stage_2 parsing finished')
    while not download.check_if_stage3_parsing_is_complete():
        entry_id = download.parse_products_parameters(number_of_products_to_parse=2)
    logging.info('Parsing is complete.')
    quit()

if __name__ == '__main__':
    main()
