# mongo db setting
import certifi
import pymongo
ca = certifi.where()
client = pymongo.MongoClient('', tlsCAFile=ca)
db = client.seoul_restroom

# 회원가입 DB
sign_up_info = {
    'user_id': "test id 1",
    'user_pw': "test pw 1",
    'nick_name': "test nickname 1"
}
db.signup.insert_one(sign_up_info)

# 상세정보 DB
detail_info = {
    'name': "test name 1",
    'address': "test adress 1",
    'star': "test star 1",
    'restroom_id' : "test id 1",
    'image_url_1': "test url 1",
    'image_url_2': "test url 2",
    'image_url_3': "test url 3",
}
db.detail.insert_one(detail_info)

# # 구이름 DB
# district_info = {
#     'gu_names' : "test gunames 1"
# }
# db.district.insert_one(district_info)
#
# # 리뷰 DB
# review_info = {
#     'comment': "test comment 1",
#     'user_id': "test id 1" # 댓글러 구분용
# }
# db.review.insert_one(review_info)