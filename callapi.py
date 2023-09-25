import config 
import requests
import json
import datetime

headers = {'content-type': 'application/json'}

def call_api(id,url):
    result = requests.post(config.api + url, headers=headers, data=json.dumps({'data':{'id': id}}))
    result = result.json()
    return result