

if __name__ == __main__:
    from downloader import Downloader
    import time
    db_config = 'postgresql://postgres:test1234@localhost:5432/oma_catalog_test'
    dwnld = Downloader(db_config, create_new_tables=False)

    if dwnld.check_if_stage1_parsing_is_complete():
        while not dwnld.check_if_stage2_parsing_is_complete():
            try:
                dwnld.parse_product_url_from_subcats_lvl2(number_of_subcats=10)
                time.sleep(0.1)
            except:
                pass
        while not dwnld.check_if_stage3_parsing_is_complete():
            try:
                dwnld.parse_products_parameters(number_of_products_to_parse=20)
                time.sleep(0.1)
            except:
                pass
        else:
            dwnld = Downloader(db_config, create_new_tables=True)
            dwnld.parse_main_catalog_page_single_run()
