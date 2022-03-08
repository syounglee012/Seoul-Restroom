from pymongo import MongoClient
import jwt
import datetime
import hashlib
import urllib.parse
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta

# login setting
app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

# mongo db setting
import certifi
import pymongo
ca = certifi.where()
client = pymongo.MongoClient('mongodb+srv://test:sparta@cluster0.6cz6m.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.dbsparta

# 페이지별 기능 구현
## 메인페이지 templates
@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])

        return render_template('index.html')
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))

@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.signup.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 1)  # 로그인 1시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')  #.decode('utf-8')삭제 (이미 decode 되었기때문에 decode 할게없음)

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,                               # 아이디
        "password": password_hash,                                  # 비밀번호
    }
    db.signup.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    username_receive = request.form['username_give']
    exists = bool(db.signup.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

##
## 구이름 list templates
# @app.route('/gu_names/<gu_name>')
# def gu_name(gu_name):
#    return render_template('{}.html'.format(gu_name))

### 구별 화장실 list templates
@app.route('/gu_names/<gu_name>') #태성 주소수정필요
def rest_list(gu_name):
   return render_template('restroom_list.html'.format(gu_name))

@app.route('/api') #태성
def rest_room_ls():
   # name, address, star, restroom_id, img_url_1, img_url_2, img_url_3 <== restroom_list
   gu_name = request.args.get('guname')
   # restroom_list = list(db.base_info.find({'adress': gu_name}, {'_id': False}))
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
                     "restroom_id": "2222",
                     "image_url_1": "test image_url_4",
                     "image_url_2": "test image_url_5",
                     "image_url_3": "test image_url_6"
                     },
                    {"name": "test name 3",
                     "address": "test address 3",
                     "star": "test star 3",
                     "restroom_id": "3333",
                     "image_url_1": "test image_url_7",
                     "image_url_2": "test image_url_8",
                     "image_url_3": "test image_url_9"
                     }]
   return jsonify({"restroom_list" : restroom_list})

## 성영님
# mainpage
@app.route('/gu_names/<gu_name>/<rest_room_id>') # 주소수정필요
def detail_home(gu_name, rest_room_id):
   return render_template('detail_page.html'.format(gu_name, rest_room_ls))

# detailpage
## review_append
@app.route("/review", methods=["POST"])
def reivew_post():
    name_receive = request.form["name_give"]
    comment_receive = request.form["comment_give"]
    star_receive = request.form['star_give']
    comment_list = list(db.review.find({},{'_id':False}))
    count = len(comment_list)+1
    doc = {
        'name': name_receive,
        'comment': comment_receive,
        'star': star_receive,
        'num':count
    }

    db.reivew.insert_one(doc)
    return jsonify({'msg':'댓글저장 완료!'})

## review_show
@app.route("/reivew", methods=["GET"])
def review_get():
    comment_list = list(db.review.find({},{'_id':False}))
    return jsonify({'comments':comment_list})


@app.route("/detail", methods=["GET"])
def detail_get():
    #star, name, address <= res_Detail
    res_Detail = db.detail.find_one({"restroom_id" : request.args.get('gu_names')},{'_id':False})
    img_list = list(db.img.find({'restroom_id' : request.args.get('gu_names')}))
    return jsonify({'details' : res_Detail,
                    'img_list' : img_list})


@app.route("/review/delete", methods=["POST"])
def bucket_undo():
    num_receive = request.form['num_give']
    db.review.delete_one({'num':int(num_receive)})
    return jsonify({'msg': '삭제완료!'})


##
if __name__ == '__main__':
   app.run('0.0.0.0',port=5000,debug=True)



































