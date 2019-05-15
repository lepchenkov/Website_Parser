from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup as BSoup
import re
import os
from db_connect import *


def simple_get(url):
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
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    print(e)

def get_soup(raw_html):
    soup = BSoup(raw_html, 'html.parser')
    return soup

def _get_category_objects(url):
    content = simple_get(url)
    soup = get_soup(content)
    objs = soup.findAll('section',\
                        {'class':\
                         'bordered-section js-accordion-group'})
    return objs

def _get_category_name(category_obj):
    name_raw = category_obj.select('section.bordered-section h2')
    name = name_raw[0].get_text()
    return name

def _get_subcat_lvl1_objects(category_obj):
    objs = category_obj.findAll('div',\
                                {'class':'catalog-all-item'})
    return objs

def _get_subcat_lvl1_name(subcat_lvl1_obj):
    name_raw = subcat_lvl1_obj.select('div.accordion-item_title a')
    name = name_raw[0].get_text()
    return name

def _get_subcat_lvl2_objects(subcat_lvl1_obj):
    objs = subcat_lvl1_obj.findAll('a',\
                                   {'class':'section-submenu-sublink'})
    return objs

def _get_subcat_lvl2_name(subcat_lvl2_obj):
    name = subcat_lvl2_obj.get_text()
    return name

def _get_subcat_lvl2_link(subcat_lvl2_obj):
    url = subcat_lvl2_obj.get('href')
    return url

def _get_subpage_urls(subcat_lvl2_soup):
    subpages = []
    button_combo_object = subcat_lvl2_soup.select('div.btn-combo div.hide a')
    for a_tag in button_combo_object:
        subpages.append(_construct_url(a_tag.attrs["href"]))
    return subpages

def _extract_product_links(soup):
    product_cards = soup.select('div.catalog-grid div.product-item_img-box')
    link_array = []
    for card in product_cards:
        link_raw = card.select('a.no-border-product')
        link = _construct_url(link_raw[0].attrs['href'])
        link_array.append(link)
    return link_array

def _construct_url(string):
    oma_url = 'https://www.oma.by'
    return oma_url + string

def get_subcat_lvl2_dict():
    url = _construct_url('/catalog/')
    category_objs = _get_category_objects(url)
    for category_obj in category_objs:
        category_name = _get_category_name(category_obj)
        subcat_lvl1_objs = _get_subcat_lvl1_objects(category_obj)
        for subcat_lvl1_obj in subcat_lvl1_objs:
            subcat_lvl1_name = _get_subcat_lvl1_name(subcat_lvl1_obj)
            subcat_lvl2_objs = _get_subcat_lvl2_objects(subcat_lvl1_obj)
            for subcat_lvl2_obj in subcat_lvl2_objs:
                subcat_lvl2_name = _get_subcat_lvl2_name(subcat_lvl2_obj)
                raw_url = _get_subcat_lvl2_link(subcat_lvl2_obj)
                subcat_lvl2_url = _construct_url(raw_url)
                subcat_lvl2_dict = {'category_name': category_name,
                                    'subcat_lvl1_name': subcat_lvl1_name,
                                    'subcat_lvl2_name' : subcat_lvl2_name,
                                    'url' : subcat_lvl2_url,
                                    }
                yield subcat_lvl2_dict

def get_product_dict():
    subcat_lvl2_dicts = get_subcat_lvl2_dict()
    for subcat_lvl2_dict in subcat_lvl2_dicts:
        content = simple_get(subcat_lvl2_dict.get('url'))
        soup = get_soup(content)
        test_subpages = _get_subpage_urls(soup)
        for subpage_url in test_subpages:
            content = simple_get(subpage_url)
            soup = get_soup(content)
            product_urls = _extract_product_links(soup)
            for product_url in product_urls:
                product_dict =	{
                                "url": product_url,
                                "category": subcat_lvl2_dict.get('category_name'),
                                "subcat_lvl1": subcat_lvl2_dict.get('subcat_lvl1_name'),
                                "subcat_lvl2": subcat_lvl2_dict.get('subcat_lvl1_name')
                                }
                yield product_dict


def _get_product_name(soup):
    name_raw = soup.select('div.page-title h1')
    name = name_raw[0].text
    return name

def _get_product_price(soup):
    price_raw = soup.select('div.product-info-box_price')
    if len(price_raw) == 0:
        return 0
    price_text_raw = price_raw[0].text
    price_text = price_text_raw.replace(" ", "")
    price = str(price_text[:7])
    price = price.replace('/','')
    price = price.replace('шт','')
    price = price.replace('ш','')
    price = price.replace('у','')
    price = price.replace('И','')
    price = price.replace('.','')
    price = price.replace('\n','')
    price = price.replace(',','.')
    price = price.replace('н','.')
    try:
        return float(price)
    except:
        return 0

def _get_description(soup):
    try:
        desc_raw = soup.select('article.catalog-item-description-txt_content')
        desc = desc_raw[0].text
        desc = desc.rstrip()
        return desc
    except:
        error_msg = 'failed_description'
        return error_msg


def _get_product_characteristics(soup):
    char_raw = soup.select('div.params-blocks')
    if len(char_raw) != 0:
        char = char_raw[0].text
        char = char.rstrip()
        char = char.rstrip('\n')
        char = char.replace('\n','')
    else:
        char = ''
    return char.rstrip(os.linesep)

def _get_similar(soup):
    return similar

def _get_product_image_link(soup):
    link_raw = soup.select('div.slider-w-preview img')
    link = _construct_url(link_raw[0].get('src'))
    return link

def _product_is_trend(soup):
    class_str = "'class':'icon special-icon special-icon__hit product-item_special'"
    hit_offer_raw = soup.findAll('span',{class_str})
    product_is_trend = len(hit_offer_raw) != 0
    return product_is_trend

def get_product_parameters(soup):
    name = _get_product_name(soup)
    price = _get_product_price(soup)
    desc = _get_description(soup)
    char = _get_product_characteristics(soup)
    similar = ''
    image_link = _get_product_image_link(soup)
    is_trend = _product_is_trend(soup)
    product_dict = {
            'product_name' : name,
            'product_price' : price,
            'product_description' : desc,
            'product_characteristics' : char,
            'similar_products' : similar,
            'product_image_link' : image_link,
            'product_is_trend' : is_trend,
            }
    return product_dict


def parse_product_info_into_db(number_of_entries_to_parse = 1):
    db = Postgres_db()
    initial_select_string = 'SELECT * FROM products_all WHERE '\
                            + 'is_parsed IS NULL LIMIT ' \
                            + str(number_of_entries_to_parse)
    entries_to_parse = db.query(initial_select_string)
    products_all = db.reflect_table('products_all')
    parsed_count = 0
    for entry in entries_to_parse:
        response = simple_get(entry.url)
        soup = get_soup(response)
        p_dict = get_product_parameters(soup)
        dt = datetime.now()
        if entry.is_parsed == None:
            update_sttm = products_all.update().where\
                         (products_all.c.id==entry.id).values\
                         (product_name = p_dict['product_name'], \
                          product_price = float(p_dict['product_price']), \
                          product_description = p_dict['product_description'], \
                          product_characteristics = p_dict['product_characteristics'], \
                          similar_products = p_dict['similar_products'], \
                          product_image_link = p_dict['product_image_link'], \
                          product_is_hit = p_dict['product_is_trend'], \
                          is_parsed = dt)
            db.query(update_sttm)
            parsed_count += 1
    return parsed_count

##########################class_implementation########################
class Parser(object):

    def get_url(self, url):
        return get(url)

    def get_soup(self, url):
        content  = self.get_url(url)
        soup = BSoup(content.text, 'html.parser')
        return soup

    def _construct_url(self, url):
        return 'https://www.oma.by' + url

    def _get_category_name(self, category_obj):
        name_raw = category_obj.select('section.bordered-section h2')
        name = name_raw[0].get_text()
        return name

    def _get_category_obj(self):
        url = self._construct_url('/catalog')
        soup = self.get_soup(url)
        objs = soup.findAll('section',\
                            {'class':\
                             'bordered-section js-accordion-group'})
        for obj in objs:
            name = self._get_category_name(obj)
            yield obj, name

    def get_categories(self):
        for _, name in self._get_category_obj():
            yield name

    def _get_subcat_lvl1_name(self,subcat_lvl1_obj):
        name_raw = subcat_lvl1_obj.select('div.accordion-item_title a')
        name = name_raw[0].get_text()
        return name

    def _get_subcat_lvl1_objects(self):
        for cat_obj, cat_name in self._get_category_obj():
            subcat_lvl1_objs = cat_obj.findAll('div',\
                                              {'class':'catalog-all-item'})
            for obj in subcat_lvl1_objs:
                name = self._get_subcat_lvl1_name(obj)
                p_name = cat_name
                yield obj, name, p_name

    def get_lvl1_subcategories(self):
        for _, name, p_name in self._get_subcat_lvl1_objects():
            yield name, p_name

    def _get_subcat_lvl2_objects(self):
        for subcat_lvl1_obj, s_lvl1_name, cat_name  in self._get_subcat_lvl1_objects():
            objs = subcat_lvl1_obj.findAll('a',\
                                          {'class':'section-submenu-sublink'})
            for obj in objs:
                name = obj.get_text()
                url = obj.get('href')
                p_name = s_lvl1_name
                g_p_name = cat_name
                yield obj, name, p_name, g_p_name

    def get_lvl2_subcategories(self):
        for _, name, p_name, g_p_name in self._get_subcat_lvl2_objects():
            yield name, p_name, g_p_name
