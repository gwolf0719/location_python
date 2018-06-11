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
def get_block(beacon_id):
    
    if mongo.db.ans.find({"beacon_id":beacon_id}).count() == 0:
        return False;
    else:
        data = mongo.db.ans.find_one({"beacon_id":beacon_id})
        return data['block'];

# 檢查題庫中有沒有值
def chk_question_bank(beacon_id,time_key):
    data = {
        "beacon_id":beacon_id,
        "time_key":time_key
    }
    count = mongo.db.question_bank.find(data).count()
    if count == 0 :
        ins = ins_question_bank(beacon_id,time_key);
        return ins;
    else:
        return True

def ins_question_bank(beacon_id,time_key):
    data = {}
    data['block'] = get_block(beacon_id)
    if data['block'] == False:
        return False;
    else:
        for dat in mongo.db.detectors.find():
            data[dat['detector_id']] = -9999;
        
        data['beacon_id'] = beacon_id
        data['time_key'] = time_key
        mongo.db.question_bank.insert(data);
        return True; 

    


def learm():
    
    col = mongo.db.data_format
    try:
        dataframe = pd.DataFrame(list(col.find()))

        return dataframe
    except Exception as e:
        return e;
    