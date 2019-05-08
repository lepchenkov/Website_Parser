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
    oma_content = simple_get(url)
    oma_soup = get_soup(oma_content)
    category_objects = oma_soup.findAll('section',\
                                        {'class':\
                                        'bordered-section js-accordion-group'})
    return category_objects

def get_category_name(category_obj):
    category_name_raw = category_obj.select('section.bordered-section h2')
    category_name = category_name_raw[0].get_text()
    return category_name

def get_subcat_lvl1_objects(category_obj):
    subcat_lvl_1_objects = category_obj.findAll('div',\
                                            {'class':'catalog-all-item'})
    return subcat_lvl_1_objects

def get_subcat_lvl1_name(subcat_lvl1_obj):
    subcat_lvl1_name_raw = subcat_lvl1_obj.select('div.accordion-item_title a')
    subcat_lvl1_name = subcat_lvl1_name_raw[0].get_text()
    return subcat_lvl1_name

# def parse_catalog_page(url):
#     category_objects = get_category_objects
#     for category_obj in category_objects:
#         category_name = get_category_name(category_obj)
#         subcats_lvl_1 = category.findAll('div',\
#                                           {'class':'catalog-all-item'})
