from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup as BSoup
import re
import os
from db_connect import Postgres_db



##########################class_implementation########################
class Parser(object):

    def _get_url(self, url):
        return get(url)

    def _get_soup(self, url):
        content  = self._get_url(url)
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
        soup = self._get_soup(url)
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
        for category_obj, category in self._get_category_obj():
            subcat_lvl1_objs = category_obj.findAll('div',\
                                              {'class':'catalog-all-item'})
            for obj in subcat_lvl1_objs:
                name = self._get_subcat_lvl1_name(obj)
                parent = category
                yield obj, name, parent

    def get_lvl1_subcategories(self):
        for _, name, parent in self._get_subcat_lvl1_objects():
            yield name, parent

    def _get_subcat_lvl2_objects(self):
        for subcat_lvl1_obj, s_lvl1_name, cat_name in self._get_subcat_lvl1_objects():
            objs = subcat_lvl1_obj.findAll('a',\
                                          {'class':'section-submenu-sublink'})
            for obj in objs:
                name = obj.get_text()
                url = self._construct_url(obj.get('href'))
                parent = s_lvl1_name
                grandparent = cat_name
                yield obj, name, parent, grandparent, url

    def get_lvl2_subcategories(self):
        for _, name, parent, grandparent, url in self._get_subcat_lvl2_objects():
            yield name, parent, grandparent, url

    def _get_subpage_urls(self, subcat_lvl2_url):
        soup = self._get_soup(subcat_lvl2_url)
        button_combo_object = soup.select('div.btn-combo div.hide a')
        for a_tag in button_combo_object:
            yield self._construct_url(a_tag.attrs["href"])

    def _extract_product_link(self, page_url):
        soup = self._get_soup(page_url)
        product_cards = soup.select('div.catalog-grid div.product-item_img-box')
        for card in product_cards:
            url_raw = card.select('a.no-border-product')
            url = self._construct_url(url_raw[0].attrs['href'])
            yield url

    def get_product_link(self):
        for name, parent, grandparent, url in self.get_lvl2_subcategories():
            for subpage_url in self._get_subpage_urls(url):
                for url in self._extract_product_link(subpage_url):
                    yield url, name, parent, grandparent
