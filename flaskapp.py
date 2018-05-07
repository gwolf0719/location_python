#coding=utf-8
#flaskapp.py
import sys
from flask import Flask,abort
from flask import jsonify
from flask import request
# from flask import pymongo
# from pymongo import MongoClient
from flask_pymongo import PyMongo
# from pymongo import MongoClient

app = Flask(__name__)

 

app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = '27017'
app.config['MONGO_DBNAME'] = 'test'
# app.config['MONGO_USERNAME'] = 'root'
# app.config['MONGO_PASSWORD'] = 'aaa2016'
# app.config['MONGO_AUTH_SOURCE'] = 'admin' 
mongo = PyMongo(app)

@app.route('/')
def index():
    return '111'

@app.route('/test/', methods=['POST'])
def api_tasks():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return 'No json data found', 400

        collection = mongo.db.test_coll
        result = {
            'json data in request': data['title']
        }
        collection.insert({'name': 'name', 'distance': 'distance'})
        return jsonify(result)

    return 'Please post json data'


if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
