#coding=utf-8
#flaskapp.py
from flask import Flask,abort

from flask import jsonify
from flask import request
import json
from flask_pymongo import PyMongo
import time
import learm

import pandas as pd
import tensorflow as tf
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
# from sklearn import datasets



app = Flask(__name__)

app.config['MONGO_HOST'] = 'localhost'
app.config['MONGO_PORT'] = '27017'
app.config['MONGO_DBNAME'] = 'location'
mongo = PyMongo(app)

@app.route('/')
def index():
    return '<b>Hello Flask A2pps</b>'


@app.route('/do_learm/')
def do_learm():
    
    dataframe = pd.DataFrame(list(mongo.db.question_bank.find()))
    data_list = []
    for dat in mongo.db.detectors.find():
        data_list.append(dat['detector_id'])

    X_train, X_test, y_train, y_test = train_test_split(dataframe[data_list], dataframe[['block']], test_size=0.3)
    
    # 隨機森林
    from sklearn.ensemble import RandomForestClassifier
    forest = RandomForestClassifier(criterion='entropy', n_estimators=100, random_state=3, n_jobs=2)
    forest.fit(X_train, y_train['block'].values)
    y_test['block'].values
    error = 0
    for i, v in enumerate(forest.predict(X_test)):
        if v != y_test['block'].values[i]:
            #print(i, v)
            error += 1
    
    # # 儲存 model
    from sklearn.externals import joblib
    joblib.dump(forest, '/var/www/html/locate.pkl')
    
    res = []
    # Accuracy
    Accuracy =  100 - (float(error) / i)*100
    res.append({"Accuracy":Accuracy})
   
    return jsonify(res)

# 設定 detector
@app.route('/learm/set_detector/',methods=['POST'])
def set_detector():
    data = request.get_json();
    # 將detector id 寫入
    learm.set_detector(data);
    data_list = [];
    # 取回 detectors
    data_list = learm.detectors();
    return jsonify(data_list)
    
# 設定答案 beacon_id,block
@app.route('/learm/set_ans/',methods=['POST'])
def set_ans():
    data = request.get_json();
    # 將detector id 寫入
    learm.set_ans(data);
    data_list = [];
    # 取回 detectors
    data_list = learm.ans_list();
    return jsonify(data_list)

# 送題庫
@app.route('/learm/send_question_bank/',methods=['POST'])
def send_question_bank():
    data = request.get_json();
    time_key = str(int(time.time()/10));
    res = []
    detectors = learm.detectors();
    # 檢查  detector_id 存在
    beacon_bank = []
    source = []

    # 檢查switch狀態
    switch_file_path = '/var/www/html/location/switch.conf';
    switch = open(switch_file_path,'r');

    if str(switch.read()) == 'on': 
        if data['detector_id'] in detectors:
            # 檢查題庫中資料有沒有這個 beacon_id
            for beacon in data['beacons']:
                source = learm.chk_question_bank(beacon['beacon_id'],time_key)
                beacon_bank_json = {
                    "beacon_id":beacon['beacon_id'],
                    "time_key":time_key
                }
                update = {
                    data['detector_id'] : beacon['beacon_rssi']
                }

                # 更新數據
                if source == True:
                    mongo.db.question_bank.update_one(beacon_bank_json,{'$set':update});
            

    
    # res.append(source);
    res.append({'beacon_bank':beacon_bank});
    res.append({'detectors':detectors});
    res.append({'time':time_key});
    # qlist = mongo.db.question_bank.find();
    # res.append({'qlist':qlist})


    return jsonify(res)
        
                
    
@app.route('/beacon_bank_switch/',methods=['GET'])
def beacon_bank_switch():
    switch = request.args.get('switch');
    file_path = '/var/www/html/location/switch.conf';
    f = open(file_path,'w+')
    f.write(switch);
    f = open(file_path,'r');
    return f.read();
    



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





if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
