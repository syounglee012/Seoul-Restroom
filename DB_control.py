# mongo db setting
import googlemaps
import hashlib
import certifi
import pymongo
ca = certifi.where()
client = pymongo.MongoClient('mongodb+srv://test:sparta@cluster0.6cz6m.mongodb.net/Cluster0?retryWrites=true&w=majority', tlsCAFile=ca)
db = client.seoul_restroom

# 회원가입 DB
sign_up_info = {
    'user_id': "test id 1",
    'user_pw': "test pw 1",
    'nick_name': "test nickname 1"
}
# db.signup.insert_one(sign_up_info)

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
# db.detail.insert_one(detail_info)



m = hashlib.sha256()
name_X_Y = list(db.district.find({},{'_id':False}))
for ls in name_X_Y:
    name_target = ls["name"]
    X = ls["X_WGS84"]
    Y = ls["Y_WGS84"]

    ## XY convert
    gmaps = googlemaps.Client(key='AIzaSyCQnVTDXq3aqasDaI0vzZkSaV18hi87nvE')
    g_list = gmaps.reverse_geocode((Y, X), language='ko')
    dis_ls = []
    for address in g_list:
        name = address["formatted_address"]
        new_Y = address["geometry"]["location"]["lat"]
        new_X = address["geometry"]["location"]["lng"]
        dis_ls.append([name, abs(new_Y - Y), abs(new_X - X)])

    dis_ls.sort(reverse=True)
    converted_address = dis_ls[0][0]

    ## Hash func
    m.update("{}{}".format(name_target, converted_address).encode('utf-8'))
    restroom_id = m.hexdigest()
    base_info = {
        'name' : name_target,
        'restroom_id' : restroom_id,
        'address' : converted_address
        }
    db.base_info.insert_one(base_info)

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