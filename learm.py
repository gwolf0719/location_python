#!/usr/bin/python
# coding:utf-8
from flask import Flask,abort

from flask import jsonify
from flask import request
import json
from flask_pymongo import PyMongo

import pandas as pd


app = Flask(__name__)

mongo = PyMongo(app)


# 設定 detetor 列表
def set_detetor(data):
    mongo.db.drop_collection('detetors');
    col = mongo.db.detetors;
    
    col.insert(data);
    return True
    



def learm():
    
    col = mongo.db.data_format
    try:
        dataframe = pd.DataFrame(list(col.find()))

        return dataframe
    except Exception as e:
        return e;
    