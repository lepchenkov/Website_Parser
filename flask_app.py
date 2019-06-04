
import sys
import os
dir_path = os.getcwd()
sys.path.insert(0,'/home/kiryl/Documents/Projects/Website_Parser')

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from db_connect import Postgres_db

db_config = 'postgresql://postgres:test1234@localhost:5432/oma_catalog_test'


app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

ma = Marshmallow(app)

@app.route('/product', methods=['GET'])
def get_product():
    id = request.json['id']
    db = Postgres_db(db_config)
    return jsonify(db.get_product_by_id(id))

if __name__ == '__main__':
    app.run(debug = True)
