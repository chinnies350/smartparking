import os,json
import requests
import celery
import redis
from producer import messagePublisher
from dotenv import load_dotenv
load_dotenv()

# redis database config
redis_client=redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))

# celery configuration
celeryWorker = celery.Celery(os.getenv('CELERY_TASKNAME'), broker=f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{os.getenv("CELERY_REDIS_DB")}')


@celeryWorker.task()
def postUserName(id,value,emailId,):
    try:
        print("postUserName called",id, value, emailId)
        redis_client.hset('userMaster', id, value, emailId)
        return 'celery working fine'
    except Exception as e:
        return str(e)


@celeryWorker.task()
def forgotMailData(mailData):
    try:
        print("forgotMailData called",mailData)
        messagePublisher.publish(queueName='notificationService', message = {
                            'action':'Password Recovery',
                            'body':{
                                'emailId': mailData[0]['emailId'],
                                'phoneNo': mailData[0]['phoneNumber'],
                                'userName':mailData[0]['userName']
                            }
                        })
        return 'celery working fine'
    except Exception as e:
        return str(e)

@celeryWorker.task()
def signUpData(mailData):
    try:
        print("signUpData called",mailData)
        messagePublisher.publish(queueName='notificationService', message = {
                            'action':'signUp',
                            'body':{
                                'emailId': mailData['emailId'],
                                'phoneNo': mailData['phoneNumber']
                            }
                        })
        return 'celery working fine'
    except Exception as e:
        return str(e)


@celeryWorker.task()
def signUpOTPData(userName,OTP,dataType):
    try:
        print("signUpOTPData called",userName,OTP)

        messagePublisher.publish(queueName='notificationService', message = {
                            'action':'OTP',
                            'body':{
                                'emailId':userName if dataType=='M' else None,
                                'phoneNo':userName if dataType=='S' else None,
                                'OTP':OTP,
                                'userName':'User'
                            }
                        })
        return 'celery working fine'
    except Exception as e:
        return str(e)


@celeryWorker.task()
def verifyOTPData(mailData,OTP):
    try:
        print("verifyOTPData called",mailData,OTP)
        messagePublisher.publish(queueName='notificationService', message = {
                            'action':'OTP',
                            'body':{
                                'emailId': mailData[0]['emailId'],
                                'phoneNo': mailData[0]['phoneNumber'],
                                'userName':mailData[0]['userName'],
                                'OTP':OTP,
                                'userId':mailData[0]['userId'],
                                'registrationToken':mailData[0]['registrationToken']
                            }
                        })
        return 'celery working fine'
    except Exception as e:
        return str(e)


@celeryWorker.task()
def userOffersData(mailData,offerId,userId):
    try:
        print("userOffersData called",mailData,offerId)
        url=f"{os.getenv('OFFER_SERVICE_URL')}/offerMaster?offerId={offerId}"
        response = requests.get(url)
        response = json.loads(response.text)
        url=f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/parkingOwnerMaster?userId={userId}"
        parkingOwnerResponse = requests.get(url)
        parkingOwnerResponse = json.loads(parkingOwnerResponse.text)
        messagePublisher.publish(queueName='notificationService', message = {
                            'action':'Offer Code',
                            'body':{
                                'emailId': mailData[0]['emailId'],
                                'phoneNo': mailData[0]['phoneNumber'],
                                'userName':mailData[0]['userName'],
                                'offerCode':response['response'][0]['offerCode'] if response.get('statusCode')==1 else None,
                                'parkingName':parkingOwnerResponse['response'][0]['parkingName'] if response.get('statusCode')==1 else None
                                
                            }
                        })
        return 'celery working fine'
    except Exception as e:
        return str(e)