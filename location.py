import requests
import json

send_url = "http://api.ipstack.com/check?access_key=b59b7469fe7eb5011c531f290a969a05"
geo_req = requests.get(send_url)
geo_json = json.loads(geo_req.text)
lat= str(geo_json['latitude'])
log = str(geo_json['longitude'])
city = str(geo_json['city'])

"""
import requests

res = requests.get('https://ipinfo.io/')
data = res.json()

city = data['city']
state = data['region']
location = data['loc'].split(',')
lat = location[0]
log = location[1]
"""
