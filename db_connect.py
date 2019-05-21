import sys
import os
from sqlalchemy import create_engine, update, text
from sqlalchemy import Column, String, Integer, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
import datetime


class Postgres_db(object):

    def __init__(self, db_config):
        self._engine = create_engine(db_config)
        self._connect = self._engine.connect()
        self._meta = MetaData(self._engine)

    def _query(self, query):
        return self._connect.execute(query)

    def _reflect_table(self, table_name):
        table = Table(table_name,
                      self._meta, autoload=True,
                      autoload_with=self._engine)
        return table

    def create_tables(self):
        categories_query = """CREATE TABLE categories
                              (id SERIAL PRIMARY KEY,
                              name VARCHAR (255) NOT NULL);"""
        self._query(categories_query)
        subcategories_lvl1_query = """CREATE TABLE subcategories_lvl1
                                      (id SERIAL PRIMARY KEY,
                                      name VARCHAR (255),
                                      category_id INT REFERENCES
                                      categories ON DELETE RESTRICT);"""
        self._query(subcategories_lvl1_query)
        subcategories_lvl2_query = """CREATE TABLE subcategories_lvl2
                                      (id SERIAL PRIMARY KEY,
                                      name VARCHAR (255) NOT NULL,
                                      url VARCHAR (255) NOT NULL,
                                      parsed_at TIMESTAMP DEFAULT NULL,
                                      subcat_lvl1_id INT NOT NULL REFERENCES
                                      subcategories_lvl1 ON DELETE RESTRICT);"""
        self._query(subcategories_lvl2_query)
        product_table_query = """CREATE TABLE products
                                 (id SERIAL PRIMARY KEY,
                                 url VARCHAR (255) NULL,
                                 name VARCHAR (255) NULL,
                                 price NUMERIC(6,2) NULL,
                                 units VARCHAR NULL,
                                 description VARCHAR NULL,
                                 image_url VARCHAR NULL,
                                 is_trend BOOLEAN NULL,
                                 parsed_at TIMESTAMP DEFAULT NULL,
                                 subcat_lvl2_id INT NOT NULL REFERENCES
                                 subcategories_lvl2 ON DELETE RESTRICT);"""
        self._query(product_table_query)
        product_properties_query = """CREATE TABLE product_properties
                                      (id SERIAL PRIMARY KEY,
                                      name VARCHAR,
                                      value VARCHAR,
                                      product_id INT NOT NULL REFERENCES
                                      products ON DELETE RESTRICT);"""
        self._query(product_properties_query)
        return True

    def drop_existing_tables_from_db(self):
        statement = """DROP TABLE categories,subcategories_lvl1,
                       subcategories_lvl2, products, product_properties;"""
        return self._query(statement)

    def get_table_names_from_database(self):
        statement = """SELECT table_name FROM information_schema.tables
                       WHERE table_schema='public'"""
        result_set = self._query(statement)
        for tablename in result_set:
            yield tablename

    def select_product_by_id(self, prod_id):
        statement = text("SELECT * FROM products WHERE id=:product_id").\
                    bindparams(product_id=prod_id)
        return self._query(statement)

    def category_item_insert(self, category_name):
        statement = text("""INSERT INTO categories
                            VALUES (nextval(pg_get_serial_sequence
                            ('categories', 'id')),
                            :category_name)
                            RETURNING id;""").\
                            bindparams(category_name=category_name)
        result = self._connect.execute(statement).fetchone()[0]
        return result

    def subcat_lvl1_insert(self, subcat_lvl1_name, parent_name):
        statement = text("""INSERT INTO subcategories_lvl1
                            VALUES (nextval(pg_get_serial_sequence
                            ('subcategories_lvl1', 'id')),
                            :name,
                            (SELECT id from categories
                            WHERE name=:parent_name));""").\
                            bindparams(name=subcat_lvl1_name,
                                       parent_name=parent_name)
        return self._query(statement)

    def subcat_lvl1_insert_no_subq(self, subcat_lvl1_name, parent_id):
        statement = text("""INSERT INTO subcategories_lvl1
                            VALUES (nextval(pg_get_serial_sequence
                            ('subcategories_lvl1', 'id')),
                            :name, :parent_id)
                            RETURNING id;""").\
                            bindparams(name=subcat_lvl1_name,
                                       parent_id=parent_id)
        result = self._connect.execute(statement).fetchone()[0]
        return result

    def subcat_lvl2_insert(self, subcat_lvl2_dict):
        statement = text("""INSERT INTO subcategories_lvl2
                            VALUES (nextval(pg_get_serial_sequence
                            ('subcategories_lvl2', 'id')),
                            :name, :url, NULL,
                            (SELECT id from subcategories_lvl1
                            WHERE name=:parent LIMIT 1));""").\
                            bindparams(name=subcat_lvl2_dict.get('name', ''),
                                       url=subcat_lvl2_dict.get('url', ''),
                                       parent=subcat_lvl2_dict.get('parent', '')
                                       )
        return self._query(statement)

    def subcat_lvl2_insert_no_subq(self, subcat_lvl2_dict, subcat_lvl1_id):
        statement = text("""INSERT INTO subcategories_lvl2
                            VALUES (nextval(pg_get_serial_sequence
                            ('subcategories_lvl2', 'id')),
                            :name, :url, NULL,
                            :parent_id);""").\
                            bindparams(name=subcat_lvl2_dict.get('name', ''),
                                       url=subcat_lvl2_dict.get('url', ''),
                                       parent_id=subcat_lvl1_id
                                       )
        return self._connect.execute(statement)

    def get_unparsed_subcat_lvl2_entry(self):
        statement = """SELECT id, url, name from subcategories_lvl2
                       WHERE parsed_at IS NULL LIMIT 1;"""
        return self._query(statement).fetchone()

    def _current_timestamp(self):
        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        return timestamp

    def update_lvl2_entry_set_parsed_at(self, entry_id):
        statement = text("""UPDATE subcategories_lvl2 SET
                            parsed_at=:timestamp
                            WHERE id=:entry_id;""").\
                            bindparams(entry_id=entry_id,
                                       timestamp=self._current_timestamp())
        return self._query(statement)

    def product_initial_insert(self, product_dict):
        statement = text("""INSERT INTO products
                            VALUES (nextval(pg_get_serial_sequence
                            ('products', 'id')),
                            :url, NULL, NULL, NULL,
                            NULL, NULL, NULL, NULL,
                            (SELECT id from subcategories_lvl2
                            WHERE name=:parent_name LIMIT 1));""").\
                            bindparams(url=product_dict.get('url', ''),
                                       parent_name=product_dict.get('parent', '')
                                       )
        return self._query(statement)

    def get_unparsed_product_entry(self):
        statement = """SELECT id, url from products
                       WHERE parsed_at IS NULL LIMIT 1;"""
        return self._query(statement).fetchone()

    def product_update(self, product_id, product_dict):
        statement = text("""UPDATE products SET
                            price=:price,
                            units=:units,
                            description=:description,
                            image_url=:image_url,
                            is_trend=:is_trend,
                            parsed_at=:timestamp
                            WHERE id=:product_id;""").\
                            bindparams(product_id=product_id,
                                       price=product_dict.get('price', ''),
                                       units=product_dict.get('product_units', ''),
                                       description=product_dict.get('description', ''),
                                       image_url=product_dict.get('image_url', ''),
                                       is_trend=product_dict.get('is_trend', ''),
                                       timestamp=self._current_timestamp()
                                       )
        return self._query(statement)

    def product_features_insert(self, feature_name, feature_value, product_id):
        statement = text("""INSERT INTO product_properties
                            VALUES (nextval(pg_get_serial_sequence
                            ('product_properties', 'id')),
                            :name, :value, :product_id);""").\
                            bindparams(name=feature_name,
                                       value=feature_value,
                                       product_id=product_id)
        return self._query(statement)
