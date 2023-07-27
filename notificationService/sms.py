# from routers.config import SMS_API_SAFETY_KEY,SMS_URL
import os
import requests
from dotenv import load_dotenv
# from fastapi.routing import APIRouter

# router=APIRouter(prefix='/sms',tags=['sms'])
# @router.post('')
def sendSMS(securitykey, MobileNumber, Message,peid,tpid):
    try:
        assert securitykey == os.getenv("SMS_API_SAFETY_KEY"), "Invalid Authorization!"
        querystring = {"userid": "prematix", "password": "matixpre", "sender": "PAYPRE",
                       "peid": peid, "tpid": tpid, "mobileno": MobileNumber, "msg": Message}
        headers = {'cache-control': "no-cache"}
        response = requests.request(
            "GET", os.getenv("SMS_URL"), headers=headers, params=querystring)
        assert response.text != None, response.text 
        return {"statusCode": 1, "response": response.text}
    except Exception as e:
        print("Exception as sendSMS ",str(e))
        return {"statusCode": 0, "response":"Server Error"}