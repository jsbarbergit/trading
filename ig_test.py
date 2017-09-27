import json
import sys
import requests
from requests.auth import HTTPDigestAuth

ig_url="https://demo-api.ig.com/gateway/deal/session"

with open(sys.argv[1]) as config_file:
    config = json.load(config_file)

print(config["user"])
print(config["pass"])
print(config["key"])
print(config["name"])
print(config["uri"])



body = '{ "identifier": "' + config["user"] + '", "password": "' + config["pass"] + '", "encryptedPassword": null }'
print(body)
response = requests.post(config["uri"], data=body,headers={"Content-Type": "application/json;charset=UTF-8", "Accept": "application/json; charset=UTF-8", "X-IG-API-KEY": config["key"], "Version": "2" })
print(response)
#sid=response.json()['platform']['login']['sessionId']   //to extract the detail from response
#print(response.text)
#print(sid)

