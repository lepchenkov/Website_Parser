
import sys
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from db_connect import Postgres_db
from db_configurator import get_config_string


db_config = get_config_string()

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

ma = Marshmallow(app)

@app.route('/product', methods=['GET'])
def get_product():
    id = request.json['id']
    db = Postgres_db(db_config)
    return jsonify(db.get_product_by_id(id))

@app.route('/subcategory_lvl_2', methods=['GET'])
def subcategory_lvl2():
    id = request.json['id']
    db = Postgres_db(db_config)
    return jsonify(db.get_subcategory_lvl_2(id))

@app.route('/subcategory_lvl_1', methods=['GET'])
def subcategory_lvl1():
    id = request.json['id']
    db = Postgres_db(db_config)
    return jsonify(db.get_subcategory_lvl_1(id))

@app.route('/category', methods=['GET'])
def category():
    id = request.json['id']
    db = Postgres_db(db_config)
    return jsonify(db.get_category(id))

@app.route('/product_property', methods=['GET'])
def product_property():
    id = request.json['id']
    db = Postgres_db(db_config)
    return jsonify(db.get_product_properties_by_product_id(id))

@app.route('/product_with_properties', methods=['GET'])
def product_with_properties():
    id = request.json['id']
    db = Postgres_db(db_config)
    return jsonify(db.get_product_with_properties(id))

if __name__ == '__main__':
    app.run(debug=True)
