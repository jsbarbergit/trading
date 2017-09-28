import json
import sys
import requests
from requests.auth import HTTPDigestAuth

#Get Config
with open(sys.argv[1]) as config_file:
    config = json.load(config_file)

#Login
ig_url="https://api.ig.com/gateway/deal/session"
body = '{ "identifier": "' + config["user"] + '", "password": "' + config["pass"] + '", "encryptedPassword": null }'
response = requests.post(config["uri"], data=body,headers={"Content-Type": "application/json;charset=UTF-8", "Accept": "application/json; charset=UTF-8", "X-IG-API-KEY": config["key"], "Version": "2" })
accountId=str(response.json()['currentAccountId'])
accountType=str(response.json()['accountType'])
sec_token=response.headers['X-SECURITY-TOKEN']
cst=response.headers['CST']
print('LOGIN Response: ' + str(response))



#Get the data
prices_payload= {"resolution": "DAY", "from": "2017-09-01", "to": "2017-09-26"}        
epic="CS.D.GBPUSD.TODAY.IP"
prices_uri="https://api.ig.com/gateway/deal/prices/" + epic
prices_headers={"Content-Type": "application/json;charset=UTF-8", "Accept": "application/json; charset=UTF-8", "X-IG-API-KEY": str(config["key"]), "Version": "3", "X-SECURITY-TOKEN": sec_token, "CST": cst }
price_response = requests.get(prices_uri, params=prices_payload, headers=prices_headers)
print(price_response)
print(price_response.text)



#Logout
logout_uri="https://api.ig.com/gateway/deal/session"
logout_headers={"Content-Type": "application/json;charset=UTF-8", "Accept": "application/json; charset=UTF-8", "X-IG-API-KEY": str(config["key"]), "Version": "1", "X-SECURITY-TOKEN": sec_token, "CST": cst, "_method": "DELETE", "IG-ACCOUNT-ID": accountId, "IG-ACCOUNT-TYPE": accountType }
logout_response = requests.get(logout_uri, headers=logout_headers, data={})
print('LOGOUT Response: ' + str(logout_response))
