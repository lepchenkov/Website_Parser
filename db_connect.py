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
                            category_id serial PRIMARY KEY,\
                            category_name VARCHAR (255) NOT NULL,\
                            );"
        self._connect.execute(categories_query)
        subcategory_lvl1_query = "CREATE TABLE subcategories_lvl1\
                                  (\
                                  subcat_lvl1_id serial PRIMARY KEY,\
                                  subcat_lvl1_name VARCHAR (255) NOT NULL,\
                                  CONSTRAINT parent FOREIGN KEY (category_id)\
                                  REFERENCES categories (category_id) MATCH SIMPLE\
                                  ON UPDATE NO ACTION ON DELETE NO ACTION\
                                  );"
        self._connect.execute(subcategory_lvl1_query)
        subcategory_lvl2_query = "CREATE TABLE subcategories_lvl2\
                                  (\
                                  subcat_lvl2_id serial PRIMARY KEY,\
                                  subcat_lvl2_name VARCHAR (255) NOT NULL,\
                                  CONSTRAINT parent FOREIGN KEY (subcategories_lvl1)\
                                  REFERENCES subcategories_lvl1 (subcat_lvl1_id) MATCH SIMPLE\
                                  ON UPDATE NO ACTION ON DELETE NO ACTION\
                                  );"
        self._connect.execute(subcategory_lvl2_query)
        product_table_query = "CREATE TABLE product_table\
                              (\
                              product_id serial PRIMARY KEY,\
                              product_url VARCHAR (255) NOT NULL,\
                              product_name VARCHAR (255) NOT NULL,\
                              product_price NUMERIC(6,2),\
                              product_description VARCHAR,\
                              product_image_url VARCHAR,\
                              product_is_trend BOOLEAN,\
                              product_parsed_at TIMESTAMP,\
                              CONSTRAINT parent FOREIGN KEY (subcategories_lvl2)\
                              REFERENCES subcategories_lvl2 (subcat_lvl2_id) MATCH SIMPLE\
                              ON UPDATE NO ACTION ON DELETE NO ACTION\
                              );"
        self._connect.execute(product_table_query)
        product_table_query = "CREATE TABLE product_table\
                              (\
                              product_property_id serial PRIMARY KEY,\
                              product_property_value VARCHAR,\
                              CONSTRAINT product FOREIGN KEY (product_id)\
                              REFERENCES product_table (product_id) MATCH SIMPLE\
                              ON UPDATE NO ACTION ON DELETE NO ACTION\
                              );"
        self._connect.execute(product_table_query)
        pass

    def select_product_by_id(self, prod_id):
        stmt = text("SELECT * FROM products_all WHERE id=:product_id")
        stmt = stmt.bindparams(product_id=prod_id)
        return self._connect.execute(stmt)
