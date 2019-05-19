import sys
import os
from sqlalchemy import create_engine, update, text
from sqlalchemy import Column, String, Integer, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime


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
        categories_query = "CREATE TABLE categories\
                            (\
                            id SERIAL PRIMARY KEY,\
                            name VARCHAR (255) NOT NULL\
                            );"
        self._connect.execute(categories_query)
        subcategories_lvl1_query = "CREATE TABLE subcategories_lvl1\
                                  (\
                                  id INTEGER PRIMARY KEY,\
                                  name VARCHAR (255) NOT NULL,\
                                  category_id INT NOT NULL REFERENCES\
                                  categories ON DELETE RESTRICT\
                                  );"
        self._connect.execute(subcategories_lvl1_query)
        subcategories_lvl2_query = "CREATE TABLE subcategories_lvl2\
                                  (\
                                  id serial PRIMARY KEY,\
                                  name VARCHAR (255) NOT NULL,\
                                  url VARCHAR (255) NOT NULL,\
                                  subcat_lvl1_id INT NOT NULL REFERENCES\
                                  subcategories_lvl1 ON DELETE RESTRICT\
                                  );"
        self._connect.execute(subcategories_lvl2_query)
        product_table_query = "CREATE TABLE products\
                              (\
                              id serial PRIMARY KEY,\
                              url VARCHAR (255) NOT NULL,\
                              name VARCHAR (255) NOT NULL,\
                              price NUMERIC(6,2),\
                              units VARCHAR,\
                              description VARCHAR,\
                              image_url VARCHAR,\
                              is_trend BOOLEAN,\
                              parsed_at TIMESTAMP,\
                              subcat_lvl2_id INT NOT NULL REFERENCES\
                              subcategories_lvl2 ON DELETE RESTRICT\
                              );"

        self._connect.execute(product_table_query)
        product_properties_query = "CREATE TABLE product_properties\
                                    (\
                                    id serial PRIMARY KEY,\
                                    name VARCHAR,\
                                    value VARCHAR,\
                                    product_id INT NOT NULL REFERENCES\
                                    products ON DELETE RESTRICT\
                                    );"
        self._connect.execute(product_properties_query)
        pass

    def drop_existing_tables_from_db(self):
        stmt = "DROP TABLE categories, subcategories_lvl1, \
                subcategories_lvl2, products, product_properties;"
        return self._connect.execute(stmt)

    def select_product_by_id(self, prod_id):
        stmt = text("SELECT * FROM products WHERE id=:product_id")
        stmt = stmt.bindparams(product_id=prod_id)
        return self._connect.execute(stmt)

    def category_item_insert(self, category_name):
        stmt = text("INSERT INTO categories\
                    VALUES (nextval(pg_get_serial_sequence('categories', 'id')),\
                    :category_name);")
        stmt = stmt.bindparams(category_name=category_name)
        return self._connect.execute(stmt)

    def subcat_lvl1_insert(self, subcat_lvl1_id, subcat_lvl1_name, parent_name):
        stmt = text("INSERT INTO subcategories_lvl2 \
                    VALUES (:subcat_lvl1_id, :subcat_lvl1_name,\
                    (SELECT id from categories WHERE name=:parent));")
        stmt = stmt.bindparams(category_id=category_id,
                               category_name=category_name,
                               parent=parent)
        return self._connect.execute(stmt)

    def subcat_lvl2_insert(self, subcat_lvl2_dict):
        stmt = text("INSERT INTO subcategories_lvl2 \
                    VALUES (:subcat_lvl2_id, :subcat_lvl2_name, \
                    :subcat_lvl2_url, \
                    (SELECT id from subcategories_lvl1 \
                    WHERE name=:parent_name));")
        stmt = stmt.bindparams(subcat_lvl2_id=category_id,
                               subcat_lvl2_name=subcat_lvl2_dict.get('name', ''),
                               subcat_lvl2_url=subcat_lvl2_dict.get('url', ''),
                               parent_name=subcat_lvl2_dict.get('parent', ''),
                               )
        return self._connect.execute(stmt)

    def product_initial_insert(self, product_id, product_dict):
        stmt = text("INSERT INTO products \
                    VALUES (:id, :url, :name, :price, :description, \
                    :image_url, :is_trend, :parsed_at,\
                    (SELECT id from subcategories_lvl2 \
                     WHERE name=:parent_name));")
        stmt = stmt.bindparams(id=category_id,
                               url=product_dict.get('url', ''),
                               name=product_dict.get('name', ''),
                               price=None,
                               description=None,
                               image_url=None,
                               is_trend=None,
                               parsed_at=None,
                               parent_name=product_dict.get('parent', '')
                               )
        return self._connect.execute(stmt)

    def product_update(self, product_id, product_dict, curr_timestamp):
        stmt = text("UPDATE products SET\
                     price=:price,\
                     units=:units,\
                     description=:description,\
                     image_url=:image_url,\
                     is_trend=:is_trend,\
                     parsed_at=:timestamp,\
                     WHERE\
                     id=:product_id,\
                     );")
        stmt = stmt.bindparams(product_id=product_id,
                               price=product_dict.get('price', ''),
                               description=product_dict.get('description', ''),
                               image_url=product_dict.get('image_url', ''),
                               is_trend=product_dict.get('is_trend', ''),
                               parent_name=product_dict.get('parent', ''),
                               timestamp=curr_timestamp
                               )
        return self._connect.execute(stmt)

    def product_feature_insert(self, product_id, feature_id,
                               feature_name, feature_value):
        stmt = text("INSERT INTO product_properties \
                    VALUES (:id, :name, :value,\
                    (SELECT id from products \
                     WHERE id=:product_id));")
        stmt = stmt.bindparams(id=feature_id,
                               name=feature_name,
                               value=feature_value,
                               product_id=product_id
                               )
        return self._connect.execute(stmt)
