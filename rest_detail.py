from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

from pymongo import MongoClient
client = MongoClient("내 URL")
db = client.sparta

# mainpage
@app.route('/')
def home():
   return render_template('restroom.html')

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



if __name__ == '__main__':
   app.run('0.0.0.0', port=8000, debug=True)