import sys
import os
from sqlalchemy import create_engine, update
from sqlalchemy import Column, String, Integer, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime



class Postgres_db(object):

    def __init__(self):
        db_config = 'postgresql://postgres:test1234@localhost:5432/oma_catalog_test'
        self._engine = create_engine(db_config)
        self._connect = self._engine.connect()
        self._meta = MetaData(self._engine)

    def query(self, query):
        return self._connect.execute(query)

    def reflect_table(self, table_name):
        table = Table(table_name, \
                     self._meta, autoload=True, \
                     autoload_with = self._engine)
        return table


##########################################################################
#A Table object can be instructed to load information about itself
#from the corresponding database schema object already existing
#within the database. This process is called reflection.
