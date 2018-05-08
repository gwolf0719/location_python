#coding=utf-8
#flaskapp.py
from flask import Flask,abort
from flask import jsonify
from flask import request

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
    return jsonify(result)
# 硬體回傳原始資料結束



if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)
