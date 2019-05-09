from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup as BSoup
import re


######## get url ############################################################
def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None

def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    """
    prints log errors
    """
    print(e)

def get_soup(raw_html):
    soup = BSoup(raw_html, 'html.parser')
    return soup

##############################################################################

def get_category_objects(url):
    content = simple_get(url)
    soup = get_soup(content)
    objs = soup.findAll('section',\
                        {'class':\
                         'bordered-section js-accordion-group'})
    return objs

def get_category_name(category_obj):
    name_raw = category_obj.select('section.bordered-section h2')
    name = name_raw[0].get_text()
    return name

def get_subcat_lvl1_objects(category_obj):
    objs = category_obj.findAll('div',\
                                {'class':'catalog-all-item'})
    return objs

def get_subcat_lvl1_name(subcat_lvl1_obj):
    name_raw = subcat_lvl1_obj.select('div.accordion-item_title a')
    name = name_raw[0].get_text()
    return name

def get_subcat_lvl2_objects(subcat_lvl1_obj):
    objs = subcat_lvl1_obj.findAll('a',\
                                   {'class':'section-submenu-sublink'})
    return objs

def get_subcat_lvl2_name(subcat_lvl2_obj):
    name = subcat_lvl2_obj.get_text()
    return name

def get_subcat_lvl2_link(subcat_lvl2_obj):
    url = subcat_lvl2_obj.get('href')
    return url


def get_subpage_urls(subcat_lvl2_soup):
    subpages = []
    button_combo_object = subcat_lvl2_soup.select('div.btn-combo div.hide a')
    for a_tag in button_combo_object:
        subpages.append('https://www.oma.by' + a_tag.attrs["href"])
    return subpages

def extract_product_links(soup):
    product_cards = soup.select('div.catalog-grid div.product-item_img-box')
    link_array = []
    for card in product_cards:
        link_raw = card.select('a.no-border-product')
        link = 'https://www.oma.by' + link_raw[0].attrs['href']
        link_array.append(link)
    return link_array

def parse_catalog_page(url):
    outp_list = []
    category_objs = get_category_objects(url)
    for category_obj in category_objs:
        category_name = get_category_name(category_obj)
        subcat_lvl1_objs = get_subcat_lvl1_objects(category_obj)
        for subcat_lvl1_obj in subcat_lvl1_objs:
            subcat_lvl1_name = get_subcat_lvl1_name(subcat_lvl1_obj)
            subcat_lvl2_objs = get_subcat_lvl2_objects(subcat_lvl1_obj)
            for subcat_lvl2_obj in subcat_lvl2_objs:
                subcat_lvl2_name = get_subcat_lvl2_name(subcat_lvl2_obj)
                outp_list.append(subcat_lvl2_name)
    return outp_list
