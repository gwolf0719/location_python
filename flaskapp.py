#coding=utf-8
#flaskapp.py
from flask import Flask,abort
from flask import jsonify
from flask import request
import json

from flask_pymongo import PyMongo

app = Flask(__name__)

app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = '27017'
app.config['MONGO_DBNAME'] = 'location'
mongo = PyMongo(app)

@app.route('/')
def index():
    return 'Hello Flask Apps'


# 硬體回傳原始資料開始
@app.route('/api_setlocation/',methods=['POST'])
def api_setlocation():
    data = request.get_json()
    col = mongo.db.raw_data
    col.insert(data)
    result = {
        'sys_code':'200',
        'sys_msg':'success'
    }
    #分散存檔
    detector_id = data.detector_id;
    time = data.time;
    for d in data.beacons:
        new_data = {
            "beacon_id":d.beacon_id,
            "beacon_rssi":d.beacon_rssi,
            "detector_id":detector_id,
            "time":time,
        }
        mongo.db.locate_list.insert(new_data)

    return jsonify(result)
# 硬體回傳原始資料結束

@app.route('/api_listlocation/')
def listlocation():
    col = mongo.db.raw_data
    output = [];
    for q in col.find().sort('time',-1).limit(50):
        output.append({'time':q['time'],'detector_id':q['detector_id']})
    return jsonify({'result':output})

@app.route('/detector_list/')
def detector_list():
    col = mongo.db.raw_data
    output = [];

    for q in col.aggregate([{"$group" : {"_id" : "$detector_id",'count': {'$sum': 1}}}]):
        output.append({'detector_id':q['_id'],'sum':q['count']})
    return jsonify({'result':output})

@app.route('/beacon_list/')
def beacon_list():
    col = mongo.db.raw_data
    output = [];
    for q in col.aggregate([{"$group" : {"_id" : "$beacon_list",'count': {'$sum': 1}}}]):
        output.append({'beacon_list':q['_id'],'sum':q['count']})
    return jsonify({'result':output})




if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
