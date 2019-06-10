import sys
import os
from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from db_connect import Postgres_db
from db_configurator import get_config_string


db_config = get_config_string()
db = Postgres_db(db_config)
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

ma = Marshmallow(app)

@app.route('/product/<product_id>', methods=['GET'])
def get_product(product_id):
    product = db.get_product_by_id(product_id)
    if len(product) == 0:
        return abort(404)
    return jsonify(product)

@app.route('/product', methods=['POST'])
def create_product():
    data = request.get_json()
    initial_product_dict = {'url': data['url'], 'parent': data['parent']}
    product_id = db.product_initial_insert(initial_product_dict)
    product_dict = {'name': data['name'],
                    'price': data['price'],
                    'product_units': data['product_units'],
                    'description': data['description'],
                    'image_url': data['image_url'],
                    'is_trend': data['is_trend']
                    }
    db.product_update(product_id, product_dict)
    return jsonify(db.get_product_by_id(product_id))

@app.route('/product/<product_id>', methods=['DELETE'])
def delete_product():
    return ''

@app.route('/subcategory_lvl_2', methods=['GET'])
def subcategory_lvl2():
    id = request.json['id']
    return jsonify(db.get_subcategory_lvl_2(id))

@app.route('/subcategory_lvl_1', methods=['GET'])
def subcategory_lvl1():
    id = request.json['id']
    return jsonify(db.get_subcategory_lvl_1(id))

@app.route('/category', methods=['GET'])
def category():
    data = request.get_json()
    id = data['id']
    get_lvl1_subcategories = data['get_lvl1_subcategories']
    get_lvl2_subcategories = data['get_lvl2_subcategories']
    if get_lvl1_subcategories is True:
        if get_lvl2_subcategories is True:
            return jsonify(db.get_category_with_lvl2_subcategories(id))
        return jsonify(db.get_category_with_lvl1_subcategories(id))
    return jsonify(db.get_category(id))

@app.route('/product_property', methods=['GET'])
def product_property():
    id = request.json['id']
    return jsonify(db.get_product_properties_by_product_id(id))

@app.route('/product_with_properties', methods=['GET'])
def product_with_properties():
    data = request.get_json()
    id = data['id']
    return jsonify(db.get_product_with_properties(id))

if __name__ == '__main__':
    app.run(debug=True)
