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


# 設定 detector 列表
def set_detector(data):
    mongo.db.drop_collection('detectors');
    ids = []
    for d in data['detector_ids']:
        data_json = {
                        'detector_id':d
                    }
        mongo.db.detectors.insert(data_json);
    return True

def detectors():
    data_list = []
    for dat in mongo.db.detectors.find():
        data_list.append(dat['detector_id'])
    return data_list;

# 設定答案
def set_ans(data):
    mongo.db.drop_collection('ans');
    ids = []
    for d in data['ans']:
        data_json = {
                        'beacon_id':d['beacon_id'],
                        'block':d['block']
                    }
        mongo.db.ans.insert(data_json);
    return True
def ans_list():
    data_list = []
    for dat in mongo.db.ans.find():
        data = {
                    'beacon_id':dat['beacon_id'],
                    'block':dat['block']
                }
        data_list.append(data)
    return data_list;


def learm():
    
    col = mongo.db.data_format
    try:
        dataframe = pd.DataFrame(list(col.find()))

        return dataframe
    except Exception as e:
        return e;
    