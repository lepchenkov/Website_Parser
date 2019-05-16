pip install flask flask-sqlalchemy flask-marshmallow marshmallow-sqlalchemy

#marshmallow-sqlalchemy package integrates marshmallow and sqlalchemy





touch app.py
##############################################################################

from flask import Flask, request, jsonify
#jsonify allows to take dict or array of python dicts and output json
from flask_alchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
#python module to deal with filepaths


#INIT app
app = Flask(__name__)

#Run Server
if __name__ == '__main__':
