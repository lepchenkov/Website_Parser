from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup as BSoup
import re
import os


class Parser(object):

    def _get_url(self, url):
        return get(url)

    def _get_soup(self, url):
        content = self._get_url(url)
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
        objs = soup.findAll('section',
                            {'class':
                             'bordered-section js-accordion-group'})
        for obj in objs:
            name = self._get_category_name(obj)
            yield obj, name

    def get_categories(self):
        for _, name in self._get_category_obj():
            yield name

    def _get_subcat_lvl1_name(self, subcat_lvl1_obj):
        name_raw = subcat_lvl1_obj.select('div.accordion-item_title a')
        name = name_raw[0].get_text()
        return name

    def _get_subcat_lvl1_objects(self):
        for category_obj, category in self._get_category_obj():
            subcat_lvl1_objs = category_obj.findAll('div',
                                                    {'class':
                                                     'catalog-all-item'})
            for obj in subcat_lvl1_objs:
                name = self._get_subcat_lvl1_name(obj)
                parent = category
                yield obj, name, parent

    def get_lvl1_subcategories(self):
        for _, name, parent in self._get_subcat_lvl1_objects():
            yield name, parent

    def _get_subcat_lvl2_objects(self):
        for subcat_lvl1_obj, s_lvl1_name, cat_name in self._get_subcat_lvl1_objects():
            objs = subcat_lvl1_obj.findAll('a',
                                           {'class':
                                            'section-submenu-sublink'})
            for obj in objs:
                name = obj.get_text()
                url = self._construct_url(obj.get('href'))
                parent = s_lvl1_name
                grandparent = cat_name
                yield obj, name, parent, grandparent, url

    def get_lvl2_subcategories(self):
        for _, name, parent, grandparent, url in self._get_subcat_lvl2_objects():
            dict_ = {
                     'name': name,
                     'parent': parent,
                     'grandparent': grandparent,
                     'url': url
                     }
            yield dict_

    def _get_subpage_urls(self, subcat_lvl2_url):
        soup = self._get_soup(subcat_lvl2_url)
        button_combo_object = soup.select('div.btn-combo div.hide a')
        for a_tag in button_combo_object:
            yield self._construct_url(a_tag.attrs["href"])

    def _extract_product_link(self, page_url):
        soup = self._get_soup(page_url)
        product_cards = soup.select('div.catalog-grid \
                                    div.product-item_img-box')
        for card in product_cards:
            url_raw = card.select('a.no-border-product')
            url = self._construct_url(url_raw[0].attrs['href'])
            yield url

    def get_product_link(self):
        for lvl2_dict in self.get_lvl2_subcategories():
            for subpage_url in self._get_subpage_urls(lvl2_dict.get('url')):
                for url in self._extract_product_link(subpage_url):
                    dict_ = {
                             'parent': lvl2_dict.get('name'),
                             'grandparent': lvl2_dict.get('parent'),
                             'grandgrandparent': lvl2_dict.get('grandparent'),
                             'url': url
                             }
                    yield dict_

    def get_product_urls_from_subcatery_lvl2_url(self, subcat_lvl2_url):
        for subpage_url in self._get_subpage_urls(subcat_lvl2_url):
            for url in self._extract_product_link(subpage_url):
                dict_ = {
                         'parent': lvl2_dict.get('name'),
                         'grandparent': lvl2_dict.get('parent'),
                         'grandgrandparent': lvl2_dict.get('grandparent'),
                         'url': url
                         }
                yield dict_

    def get_product_parameters(self, url):
        soup = self._get_soup(url)
        name = self._get_product_name(soup)
        price = self._get_product_price(soup)
        desc = self._get_description(soup)
        char = self._get_product_characteristics(soup)
        image_url = self._get_product_image_url(soup)
        is_trend = self._product_is_trend(soup)
        product_dict = {
                'name': name,
                'price': price,
                'description': desc,
                'characteristics': char,
                'similar_products': '',
                'image_url': image_url,
                'is_trend': is_trend,
                }
        return product_dict

    def _get_product_name(self, soup):
        name_raw = soup.select('div.page-title h1')
        name = name_raw[0].text
        return name

    def _get_product_price(self, soup):
        try:
            price_div = soup.select('div.product-info-box_price')
            price_fraction_raw = soup.select('div.product-info-box_price\
                                             small')
            price_fraction = price_fraction_raw[0].string
            product_unit_raw = soup.select('div.product-info-box_price\
                                            span.product-unit')
            product_unit = product_unit_raw[0].string
            price_integer = price_div[0].contents[0].strip().replace(',', '')
            product_price = float(price_integer + '.' + price_fraction)
            price_dict = {
                         'product_price': product_price,
                         'product units': product_unit
                         }
            return price_dict
        except:
            return None

    def _get_description(self, soup):
        try:
            search_string = 'article.catalog-item-description-txt_content'
            desc_raw = soup.select(search_string)
            desc = desc_raw[0].text.rstrip().replace('\n', ' ')
            desc = re.sub(' +', ' ', desc)
            return desc
        except:
            error_msg = 'failed_description'
            return error_msg

    def _get_product_characteristics(self, soup):
        charact_list = []
        charact_value_list = []
        characteristics = soup.select('li.params-block_list-item \
                                      span.param-item_name')
        characteristic_values = soup.select('span.param-item_value-col')

        for char_ in characteristics:
            charact_list.append(char_.contents[0])

        for char_value in characteristic_values:
            value = str(char_value.get_text()).strip('\n\t')
            charact_value_list.append(value)

        return dict(zip(charact_list, charact_value_list))

    def _get_product_image_url(self, soup):
        url_raw = soup.select('div.slider-w-preview img')
        url = self._construct_url(url_raw[0].get('src'))
        return url

    def _product_is_trend(self, soup):
        class_str = "'class':'icon special-icon \
                    special-icon__hit product-item_special'"
        hit_offer_raw = soup.findAll('span', {class_str})
        product_is_trend = len(hit_offer_raw) != 0
        return product_is_trend
