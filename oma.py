if __name__ == __main__:

    from downloader import Downloader
    from db_configurator import get_config_string

    db_config = get_config_string()

    dwnld = Downloader(db_config, create_new_tables=False)

    if not dwnld.check_if_stage1_parsing_is_complete():
        dwnld = Downloader(db_config, create_new_tables=True)
        dwnld.parse_main_catalog_page_single_run()

    while not dwnld.check_if_stage2_parsing_is_complete():
        dwnld.parse_product_url_from_subcats_lvl2(number_of_subcats=1)

    while not dwnld.check_if_stage3_parsing_is_complete():
        entry_id = dwnld.parse_products_parameters(number_of_products_to_parse=2)
