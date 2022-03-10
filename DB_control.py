# mongo db setting
import googlemaps
import hashlib
import certifi
import pymongo
ca = certifi.where()
client = pymongo.MongoClient('', tlsCAFile=ca)
db = client.seoul_restroom


base_ls_s = list(db.base_info.find({}, {"_id":False}))
base_ls = base_ls_s[0:1000] #1000:2000, 2000:3000, 3000:4000, 4000:
count = 0 #1000, 2000, 3000, 4000,
for base in base_ls:
    base_name = base["name"]
    count += 1
    print(count)
    db.district.update_one({'name':base_name},{'$set':{"restroom_id":count}})

# name_X_Y_ls = list(db.district.find({},{'_id':False}))
# name_X_Y = name_X_Y_ls[4000:] # 4000:
# count = 4000 # 4000
# for ls in name_X_Y:
#     name_target = ls["name"]
#     X = ls["X_WGS84"]
#     Y = ls["Y_WGS84"]
#
#     ## XY convert
#     gmaps = googlemaps.Client(key='')
#     g_list = gmaps.reverse_geocode((Y, X), language='ko')
#
#     dis_ls = []
#     for address in g_list:
#         name = address["formatted_address"]
#         new_Y = address["geometry"]["location"]["lat"]
#         new_X = address["geometry"]["location"]["lng"]
#         dis_ls.append([name, abs(new_Y - Y), abs(new_X - X)])
#
#     dis_ls.sort(reverse=True)
#     converted_address = dis_ls[0][0] ## 한국 주소
#     count += 1
#     print(count)
#
#     restroom_id = count
#     base_info = {
#         'name' : name_target,
#         'restroom_id' : restroom_id,
#         'address' : converted_address
#         }
#     db.base_info.insert_one(base_info)