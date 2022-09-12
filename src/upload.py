import requests
import os
import json

current_path = '.'
# current_path = os.path.dirname(os.path.abspath(__file__))

def upload(name):
    f = open(current_path+"/result/final/"+name) 
    # 直接給Forder/xxx.json
    table_info = json.load(f)
    res = requests.post(
        f"https://data.mongodb-api.com/app/dinorealm-dqist/endpoint/addImgData",
        json = table_info
    )

print('doing...')
upload('BAKAJOHN#000A.json')
upload('BAKAJOHN#000B.json')
upload('BAKAJOHN#000C.json')
print('done')