# python flask setting
from flask import Flask, render_template, jsonify, request, redirect, url_for
app = Flask(__name__)

# login setting
import jwt
import datetime
import hashlib
from datetime import datetime, timedelta
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"
SECRET_KEY = ''

# mongo db setting
import certifi
import pymongo
ca = certifi.where()
client = pymongo.MongoClient('', tlsCAFile=ca)
db = client.seoul_restroom

###########-*/ Code Start /*-###########
###########-*/ 페이지별 기능 구현 /*-#####
## 메인페이지 templates
# 로그인 상태 유지
@app.route('/')
def home():
    # cookies -> token 요청
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

# 로그인 서버
# 클라이언트 -> 서버 검증요청 ->ID,PW 존재여부 확인
@app.route('/sign_in', methods=['POST'])
def sign_in():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    # Password 암호화
    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    # ID, password 존재여부 확인
    result = db.signup.find_one({'username': username_receive, 'password': pw_hash})

    # ID, PW 매칭여부 확인
    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 1)  # 로그인 1시간 유지
        }
        # JWT 토큰 발행
        # .decode('utf-8')삭제->이미 decode 되었기때문에 decode 할게없다고함
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')
        # JWT 토큰 -> 클라이언트로 발행
        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})
# 회원가입 서버
@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']
    # Password -> sha256 함수로 암호화 하여 DB 저장
    password_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    doc = {
        "username": username_receive,   # 아이디
        "password": password_hash,      # 비밀번호
    }
    # ID, PW 서버로 저장
    db.signup.insert_one(doc)
    return jsonify({'result': 'success'})

# ID 중복확인
@app.route('/sign_up/check_dup', methods=['POST'])
def check_dup():
    # DB에서 user_name을 받는다.
    username_receive = request.form['username_give']
    # DB에서 user_name이 받아지면 exists (이미 존재함), bool = False를 의미
    exists = bool(db.signup.find_one({"username": username_receive}))
    return jsonify({'result': 'success', 'exists': exists})

## 화장실 list page
# url에 <gu_name>로 동적으로 요청 받아줌
# 문법상 함수 정의에서 인자로 넣어주어야하나 사용안하니 None으로 값 죽이기
@app.route('/gu_names/<gu_name>')
def rest_list(gu_name=None):
    # 화장실 리스트가 작성되어있는 html을 클라이언트로 뿌려줌
    return render_template('restroom_list.html')

# restroom_list.html파일에서 요구하는 데이터를 SSR방식으로 클라이언트로 전달
@app.route('/api/') #태성
def rest_room_ls():
   # 클라이언트가 /api?guname=${guname}으로 GET요청할때 보내준 guname값을 gu_name으로변수화
   gu_name = request.args.get('guname')
   # base_info 컬렉션에서 "address"라는 key에대한 value가 gu_name변수에 할당되어있는 문자열을 포함하고 있다면 restroom_list로 리스트형태로 할당
   # restroom_list ==> name, address, restroom_id
   restroom_list = list(db.base_info.find({ 'address' : { '$regex' : str(gu_name), '$options' : 'i' } }, {'_id': False}))
   # restroom_list리스트를 클라이언트로 전달
   return jsonify({"restroom_list" : restroom_list})

## 화장실 detail page
# url에 <gu_name>, <rest_room_id>로 동적으로 요청 받아줌
# 문법상 함수 정의에서 인자로 넣어주어 gu_name은 형식상 사용, rest_room_id는 기능상 사용
@app.route('/gu_names/<gu_name>/<rest_room_id>')
def detail_home(gu_name, rest_room_id):
    # GET요청할때 보내준 <rest_room_id>값을
    # district 컬렉션에서 "restroom_id"라는 키에대한 키값으로 활용 후 map_id_info변수로 할당
    # map_id_info ==> name, X, Y, restroom_id
    map_id_info = db.district.find_one({"restroom_id" : int(rest_room_id)}, {'_id': False})
    # detail_page.html을 랜더링해주고, id와 map_id_info라는 이름으로 클라이언트 측에 데이터를 전송
    return render_template('detail_page.html'.format(gu_name), id=rest_room_id, map_id_info=map_id_info)

## 화장실 detail info api
# detail_page.html파일에서 요구하는 데이터를 SSR방식으로 클라이언트로 전달
@app.route("/detail_api", methods=["GET"])
def detail_get():
    # detail_page에서 /detail_api?id=${rest_id}로 GET요청할때 보내준 id값을
    # base_info 컬렉션에서 "restroom_id"라는 키에대한 키값으로 활용 후 res_Detail 변수로 할당
    res_Detail = db.base_info.find_one({"restroom_id" : int(request.args.get('id'))},{'_id':False})
    # 클라이언트에 필요한 데이터를 JSON형식으로 전달
    return jsonify({'details' : res_Detail})

## 화장실 review append
# 리뷰내용을 post요청으로 review컬렉션에 저장
@app.route("/review", methods=["POST"])
def reivew_post():
    # 클라이언트에서 전달받은 데이터를 적당한 이름으로 변수화
    name_receive = request.form["name_give"]
    comment_receive = request.form["comment_give"]
    star_receive = request.form['star_give']
    rest_id = request.form["rest_id"]

    comment_list = list(db.review.find({},{'_id':False}))
    count = len(comment_list)+1
    doc = {
        'name': name_receive,        # 화장실 이름
        'comment': comment_receive,  # 리뷰comment
        'star': star_receive,        # 리뷰별점
        'num':count,                 # 게시물 삭제를 위한 인덱싱 번호
        "rest_id" : rest_id          # 화장실 고유 id
    }
    db.review.insert_one(doc)        # dictionary형태로 저장
    # alert 메세지 출력을 위하여 전송
    return jsonify({'msg': '댓글저장 완료!'})

## 화장실 review info api
# 리뷰를 get요청시 화장실 id로 검색하여 클라이언트로 결과전달
@app.route("/review_api", methods=["GET"])
def review_get():
    # detail_page에서 /review_api?id=${rest_id}로 GET요청할때 보내준 id값을
    # review 컬렉션에서 "rest_id"라는 키에대한 키값으로 활용 후 comment_list 변수로 할당
    comment_list = list(db.review.find({"rest_id" : request.args.get("id")},{'_id':False}))
    # 클라이언트에 필요한 데이터를 JSON형식으로 전달
    return jsonify({'comments':comment_list})

## 화장실 review 삭제
# 리뷰마다 부여된 num을 인덱스로 하여 컬렌션에서 삭제
@app.route("/review/delete", methods=["POST"])
def bucket_undo():
    # 클라에서 전달받은 데이터를 num_receive 변수로 할당
    num_receive = request.form['num_give']
    # review 컬렉션에서 'num'이라는 키의 키값으로 num_receive와 일치하는 Document를 삭제
    db.review.delete_one({'num':int(num_receive)})
    # alert 메세지 출력을 위하여 전송
    return jsonify({'msg': '삭제완료!'})

if __name__ == '__main__':
   app.run('0.0.0.0',port=5000, debug=True)