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

    def query(self, query):
        return self._connect.execute(query)

    def reflect_table(self, table_name):
        table = Table(table_name,
                      self._meta, autoload=True,
                      autoload_with=self._engine)
        return table

    def create_tables(self):
        category_stmt = text("CREATE TABLE Catergories \
                             (Category_id int, \
                              Category_name varchar(255),)")
        pass

    def select_item_by_id(self, prod_id):
        stmt = text("SELECT * FROM products_all WHERE id=:product_id")
        stmt = stmt.bindparams(product_id=prod_id)
        return self._connect.execute(stmt)
