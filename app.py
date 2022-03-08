# flask setting
from flask import Flask, render_template, request, jsonify, json
import certifi
import time
app = Flask(__name__)

# mongo db setting
import certifi
import pymongo
ca = certifi.where()
client = pymongo.MongoClient('', tlsCAFile=ca)
db = client.dbsparta


# 페이지별 기능 구현
## 메인페이지 templates
@app.route('/') #현승님
def home():
   return render_template('main.html')

## 구이름 list templates
@app.route('/gu_names') #준기님
def gu_names():
   return render_template('gu_list.html')

### 구별 화장실 list templates
@app.route('/gu_names/<gu_name>') #태성
def gu_name(gu_name):
   return render_template('restroom_list.html'.format(gu_name))

@app.route('/api/')
def rest_room_ls():
   # name, address, star, restroom_id, img_url_1, img_url_2, img_url_3 <== restroom_list
   gu_name = request.args.get('guname')
   # restroom_list = list(db.detail.find({'adress': gu_name}, {'_id': False}))
   restroom_list = [{"name" : "test name 1",
                    "address" : "test address 1",
                    "star": "test star 1",
                    "restroom_id": "test restroom_id 1",
                    "image_url_1": "test image_url_1",
                    "image_url_2": "test image_url_2",
                    "image_url_3": "test image_url_3"
                    },
                    {"name": "test name 2",
                     "address": "test address 2",
                     "star": "test star 2",
                     "restroom_id": "test restroom_id 2",
                     "image_url_1": "test image_url_4",
                     "image_url_2": "test image_url_5",
                     "image_url_3": "test image_url_6"
                     },
                    {"name": "test name 3",
                     "address": "test address 3",
                     "star": "test star 3",
                     "restroom_id": "test restroom_id 3",
                     "image_url_1": "test image_url_7",
                     "image_url_2": "test image_url_8",
                     "image_url_3": "test image_url_9"
                     }]
   return jsonify({"restroom_list" : restroom_list})


if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)



































