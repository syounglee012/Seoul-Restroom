from pymongo import MongoClient
import jwt
import datetime
import hashlib
import urllib.parse
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import time

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
db = client.seoul_restroom

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

### 구별 화장실 list templates
@app.route('/gu_names/<gu_name>') #태성
def rest_list(gu_name=None):
    return render_template('restroom_list.html')

@app.route('/api/') #태성
def rest_room_ls():
   # name, address, restroom_id <== restroom_list
   gu_name = request.args.get('guname')
   restroom_list = list(db.base_info.find({ 'address' : { '$regex' : str(gu_name), '$options' : 'i' } }, {'_id': False}))
   return jsonify({"restroom_list" : restroom_list})

## 성영님
# detail_mainpage
@app.route('/gu_names/<gu_name>/<rest_room_id>')
def detail_home(gu_name, rest_room_id):
    map_id_info = db.district.find_one({"restroom_id" : int(rest_room_id)}, {'_id': False})
    return render_template('detail.html'.format(gu_name), id=rest_room_id, map_id_info=map_id_info)
# detail_info_api
@app.route("/detail_api", methods=["GET"])
def detail_get():
    #int 안에 변수들이 NoneType이 들어옴
    res_Detail = db.base_info.find_one({"restroom_id" : int(request.args.get('id'))},{'_id':False})
    return jsonify({'details' : res_Detail})

# 리뷰를 post할때 화장실 id와 함께 db 저장
## review_append
@app.route("/review", methods=["POST"])
def reivew_post():
    name_receive = request.form["name_give"]
    comment_receive = request.form["comment_give"]
    star_receive = request.form['star_give']
    rest_id = request.form["rest_id"]

    comment_list = list(db.review.find({},{'_id':False}))
    count = len(comment_list)+1
    doc = {
        'name': name_receive,
        'comment': comment_receive,
        'star': star_receive,
        'num':count,
        "rest_id" : rest_id
    }
    db.review.insert_one(doc)
    return jsonify({'msg': '댓글저장 완료!'})

# 리뷰를 get 할때 화장실 id로 검색하여 클라로 결과전달
## review_info_api
@app.route("/review_api", methods=["GET"])
def review_get():
    comment_list = list(db.review.find({"rest_id" : request.args.get("id")},{'_id':False}))
    return jsonify({'comments':comment_list})

@app.route("/review/delete", methods=["POST"])
def bucket_undo():
    num_receive = request.form['num_give']
    db.review.delete_one({'num':int(num_receive)})
    return jsonify({'msg': '삭제완료!'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000, debug=True)


































