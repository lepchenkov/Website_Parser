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

@app.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product = db.get_product_by_id(product_id)
    if len(product) == 0:
        return abort(404)
    return jsonify(product)

@app.route('/products/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    db.remove_entry_from_product_table(product_id)
    return jsonify({'message': 'product removed'})

@app.route('/products/<product_id1>-<product_id2>', methods=['GET'])
def get_products_interval(product_id1, product_id2):
    products = db.get_products_interval(product_id1, product_id2)
    if len(products) == 0:
        return abort(404)
    return jsonify(products)

@app.route('/products/<product_id>/properties', methods=['GET'])
def get_product_properties(product_id):
    product = db.get_product_properties(product_id)
    if len(product) == 0:
        return abort(404)
    return jsonify(product)

@app.route('/products/price', methods=['GET'])
def get_products_filtered():
    low = float(request.args['low'])
    high = float(request.args['high'])
    product = db.get_products_filtered_by_price(low, high)
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




@app.route('/categories/<category_id>', methods=['GET'])
def get_category(category_id):
    category = db.get_category(category_id)
    if len(category) == 0:
        return abort(404)
    return jsonify(category)

@app.route('/categories/<category_id>', methods=['DELETE'])
def delete_category(category_id):
    db.remove_category(category_id)
    return jsonify({'message': 'category removed'})

@app.route('/categories/<category_id1>-<category_id2>', methods=['GET'])
def get_category_interval(category_id1, category_id2):
    category = db.get_category_interval(category_id1, category_id2)
    if len(category) == 0:
        return abort(404)
    return jsonify(category)

@app.route('/categories/<category_id>/subcategories-level1', methods=['GET'])
def get_subcategories_lvl1(category_id):
    subcategories_level1 = db.get_subcategories_lvl1(category_id)
    if len(subcategories_level1) == 0:
        return abort(404)
    return jsonify(subcategories_level1)

if __name__ == '__main__':
    app.run(debug=True)
