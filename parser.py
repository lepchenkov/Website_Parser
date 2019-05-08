import requests
import urllib.request
import time
from bs4 import BeautifulSoup as BSoup
import pandas as pd
import re


def remove_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def test_print():
    return ('it works')

def parse_main_catalog_page():
    main_page_links_df = pd.DataFrame(columns = ['Category',\
                                             'Subcategory lvl 1',\
                                             'Subcategory lvl 2',\
                                             'Link'])
    url = 'https://www.oma.by/catalog/'
    oma_main_html = requests.get(url)
    oma_catalog_soup = BSoup(oma_main_html.text, 'html.parser')
    categories = oma_catalog_soup.findAll('section',\
                                      {'class':'bordered-section \
                                      js-accordion-group'})
    i = 0;
    for category in categories:
        category_name_raw = category.select('section.bordered-section h2')
        category_name = remove_tags(str(category_name_raw[0]))
        subcats_lvl_1 = category.findAll('div',\
                                          {'class':'catalog-all-item'})
        for subcat_lvl_1 in subcats_lvl_1:
            subcat_lvl_1_name_raw = subcat_lvl_1.select('div.accordion-item_title a')
            subcat_lvl_1_name = extract_category_name(subcat_lvl_1_name_raw)
            subcats_lvl_2_tags = subcat_lvl_1.findAll('a',\
                                          {'class':'section-submenu-sublink'})

            for subcat_lvl_2_tag in subcats_lvl_2_tags:
                subcat_lvl_2_name = remove_tags(str(subcat_lvl_2_tag))
                link = 'https://www.oma.by' + subcat_lvl_2_tag.get('href')
                main_page_links_df.loc[i] = [category_name] \
                                            + [subcat_lvl_1_name] \
                                            + [subcat_lvl_2_name] + [link]
                i+=1

    return main_page_links_df
