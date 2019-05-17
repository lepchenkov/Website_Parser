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
                            id serial PRIMARY KEY,\
                            name VARCHAR (255) NOT NULL,\
                            );"
        self._connect.execute(categories_query)
        subcategories_lvl1_query = "CREATE TABLE subcategories_lvl1\
                                  (\
                                  id serial PRIMARY KEY,\
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
                              description VARCHAR,\
                              image_url VARCHAR,\
                              is_trend BOOLEAN,\
                              parsed_at TIMESTAMP,\
                              subcat_lvl2_id INT NOT NULL REFERENCES\
                              subcategories_lvl2 ON DELETE RESTRICT\
                              );"
        self._connect.execute(product_table_query)
        product_properties_query = "CREATE TABLE product_table\
                                    (\
                                    id serial PRIMARY KEY,\
                                    name VARCHAR,\
                                    value VARCHAR,\
                                    product_id INT NOT NULL REFERENCES\
                                    products ON DELETE RESTRICT\
                                    );"
        self._connect.execute(product_properties_query)
        pass

    def select_product_by_id(self, prod_id):
        stmt = text("SELECT * FROM products_all WHERE id=:product_id")
        stmt = stmt.bindparams(product_id=prod_id)
        return self._connect.execute(stmt)

    def category_item_insert(self, category_id, category_name):
        stmt = text("INSERT INTO categories (id, name) \
                    VALUES (:category_id, :category_name);")
        stmt = stmt.bindparams(category_id=category_id,
                               category_name=category_name)
        return self._connect.execute(stmt)

    def subcat_lvl1_insert(self, subcat_lvl1_id, subcat_lvl1_name, parent):
        stmt = text("INSERT INTO subcategories_lvl2 (id, name) \
                    VALUES (:subcat_lvl1_id, :subcat_lvl1_name,\
                    (SELECT id from categories WHERE name=:parent));")
        stmt = stmt.bindparams(category_id=category_id,
                               category_name=category_name,
                               parent=parent)
        return self._connect.execute(stmt)
