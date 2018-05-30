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
    return '<b>Hello Flask A2pps</b>'

# 設定答案
@app.route('/api_setans/')
def set_ans():
    return "set_ans"
# 設定 detector
@app.route('/api_setdetector/')
def setdetector():
    return "setdetector"


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

    # 轉換陣列標準資料
    output = []
    for d in data['beacons']:
        data_json = {
                        'beacon_id':d['beacon_id'],
                        'beacon_rssi':d['beacon_rssi'],
                        'detector_id':data['detector_id'],
                        "time":data['time']
                        # "block":data['block']
                    }
        mongo.db.data_format.insert(data_json)
        output.append(data_json)


    return jsonify(result)
# 硬體回傳原始資料結束


@app.route('/api_listlocation/')
def listlocation():
    col = mongo.db.data_format
    output = [];
    for q in col.find().sort('time',-1).limit(10):
        output.append({'time':q['time'],'detector_id':q['detector_id']})
    return jsonify({'result':output})

@app.route('/detector_list/')
def detector_list():
    col = mongo.db.data_format
    output = [];
    html = ''
    for q in col.aggregate([{"$group" : {"_id" : "$detector_id",'count': {'$sum': 1}}}]):
        # output.append({'detector_id':q['_id'],'sum':q['count']})
        html = html + '<li><a href="/detector_beacon_list/'+q['_id']+'/">'+q['_id']+'</a></li>';
    html = '<ul>'+html+'</ul>';
    return html

@app.route('/detector_beacon_list/<detector>/')
def detector_beacon_list(detector):
    col = mongo.db.data_format
    output = [];
    
    html = ''
    for d in col.find({'detector_id':detector}).sort('time',-1).limit(10):
        output.append({'time':d['time'],'beacon_id':d['beacon_id']})
        html = html + '<li><span>'+d['time']+'</span> | <span>'+d['beacon_id']+'</span></li>';
    html = '<ul>'+html+'</ul>';
    # return jsonify({'result':output})
    return html

@app.route('/beacon_list/')
def beacon_list():
    col = mongo.db.data_format
    output = [];
    for q in col.aggregate([{"$group" : {"_id" : "$beacon_id",'count': {'$sum': 1}}}]):
        output.append({'beacon_id':q['_id'],'sum':q['count']})
    return jsonify({'result':output})

@app.route('/learm/')
def learm():
    import learm
    
    # print learm.learm().head(5)
    learm.learm().head(5)




if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
