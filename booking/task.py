import os
from dotenv import load_dotenv
import celery
import redis
# from producer import messagePublisher
import requests,json
load_dotenv()

# redis database config
redis_client=redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))

# celery configuration
celeryWorker = celery.Celery(os.getenv('CELERY_TASKNAME'), broker=f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{os.getenv("CELERY_REDIS_DB")}')

@celeryWorker.task()
def passlot(queueName, message):
    return 'celery working fine'
    # eventServerProducer.publish(queueName, json.loads(message)))


@celeryWorker.task()
def bookingmail(userId):
    try:
        print("bookingmail called",userId)
    
        url=f"{os.getenv('USER_SERVICE_URL')}/userMaster?userId={userId}"
        response = requests.get(url)
        response = json.loads(response.text)
        url=f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/parkingOwnerMaster?userId={userId}"
        parkingOwnerResponse = requests.get(url)
        parkingOwnerResponse = json.loads(parkingOwnerResponse.text)
        messagePublisher.publish(queueName='notificationService', message = {
                        'action':'booking',
                        'body':{
                            'emailId': response['response'][0]['emailId'] if response.get('statusCode')==1 else None,
                            'phoneNo': response['response'][0]['phoneNumber'] if response.get('statusCode')==1 else None,
                            'userName':response['response'][0]['userName'] if response.get('statusCode')==1 else None,
                            'userId':response['response'][0]['userId'] if response.get('statusCode')==1 else None,
                            'registrationToken':response['response'][0]['registrationToken'] if response.get('statusCode')==1 else None,
                            'parkingName':parkingOwnerResponse['response'][0]['parkingName'] if response.get('statusCode')==1 else None,
                            'link':'http://prematix.tech/summaryPage'
                            
                        }
                    })
        return 'celery working fine'
    except Exception as e:
        return str(e)

@celeryWorker.task()
def bookingdatetimeExtendmail(mailData):
    try:
        for i in mailData:
            print("bookingdatetimeExtendmail called",mailData)
        
            url=f"{os.getenv('USER_SERVICE_URL')}/userMaster?userId={i['userId']}"
            response = requests.get(url)
            response = json.loads(response.text)
            url=f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/parkingOwnerMaster?userId={i['userId']}"
            parkingOwnerResponse = requests.get(url)
            parkingOwnerResponse = json.loads(parkingOwnerResponse.text)
            messagePublisher.publish(queueName='notificationService', message = {
                            'action':'bookingDateTimeExtendmail',
                            'body':{
                                'emailId': response['response'][0]['emailId'] if response.get('statusCode')==1 else None,
                                'phoneNo': response['response'][0]['phoneNumber'] if response.get('statusCode')==1 else None,
                                'userName':response['response'][0]['userName'] if response.get('statusCode')==1 else None,
                                'parkingName':parkingOwnerResponse['response'][0]['parkingName'] if response.get('statusCode')==1 else None,
                                'vehicleTypeName':mailData[0]['vehicleTypeName']
                                
                            }
                        })
            return 'celery working fine'
    except Exception as e:
        return str(e)


@celeryWorker.task()
def putbookingpaidAmountdmail(mailData):
    try:
        for i in mailData:
            print("putbookingpaidAmountdmail called",mailData)
        
            url=f"{os.getenv('USER_SERVICE_URL')}/userMaster?userId={i['userId']}"
            response = requests.get(url)
            response = json.loads(response.text)
            url=f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/parkingOwnerMaster?userId={i['userId']}"
            parkingOwnerResponse = requests.get(url)
            parkingOwnerResponse = json.loads(parkingOwnerResponse.text)
            messagePublisher.publish(queueName='notificationService', message = {
                            'action':'bookingpaidAmountmail',
                            'body':{
                                'emailId': response['response'][0]['emailId'] if response.get('statusCode')==1 else None,
                                'phoneNo': response['response'][0]['phoneNumber'] if response.get('statusCode')==1 else None,
                                'userName':response['response'][0]['userName'] if response.get('statusCode')==1 else None,
                                'parkingName':parkingOwnerResponse['response'][0]['parkingName'] if response.get('statusCode')==1 else None,
                                'vehicleTypeName':mailData[0]['vehicleTypeName']
                                
                            }
                        })
            return 'celery working fine'
    except Exception as e:
        return str(e)

@celeryWorker.task()
def putPaymentStatusmail(mailData):
    try:
        for i in mailData:
            print("putPaymentStatusmail called",mailData)
        
            url=f"{os.getenv('USER_SERVICE_URL')}/userMaster?userId={i['userId']}"
            response = requests.get(url)
            response = json.loads(response.text)
            url=f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/parkingOwnerMaster?userId={i['userId']}"
            parkingOwnerResponse = requests.get(url)
            parkingOwnerResponse = json.loads(parkingOwnerResponse.text)
            messagePublisher.publish(queueName='notificationService', message = {
                            'action':'paymentstatusmail',
                            'body':{
                                'emailId': response['response'][0]['emailId'] if response.get('statusCode')==1 else None,
                                'phoneNo': response['response'][0]['phoneNumber'] if response.get('statusCode')==1 else None,
                                'userName':response['response'][0]['userName'] if response.get('statusCode')==1 else None,
                                'parkingName':parkingOwnerResponse['response'][0]['parkingName'] if response.get('statusCode')==1 else None,
                                'vehicleTypeName':mailData[0]['vehicleTypeName']
                                
                            }
                        })
            return 'celery working fine'
    except Exception as e:
        return str(e)


@celeryWorker.task()
def vehicleHeaderDetailsmail(mailData,type):
    try:
        for i in mailData:
        
            print("vehicleHeaderDetailsmail called",mailData)
        
            url=f"{os.getenv('USER_SERVICE_URL')}/userMaster?userId={i['userId']}"
            response = requests.get(url)
            response = json.loads(response.text)
            url=f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/parkingOwnerMaster?userId={i['userId']}"
            parkingOwnerResponse = requests.get(url)
            parkingOwnerResponse = json.loads(parkingOwnerResponse.text)            
            if type=='I':
                messagePublisher.publish(queueName='notificationService', message = {
                                'action':'vehicleIntimemail',
                                'body':{
                                    'emailId': response['response'][0]['emailId'] if response.get('statusCode')==1 else None,
                                    'phoneNo': response['response'][0]['phoneNumber'] if response.get('statusCode')==1 else None,
                                    'userName':response['response'][0]['userName'] if response.get('statusCode')==1 else None,
                                    'userId':response['response'][0]['userId'] if response.get('statusCode')==1 else None,
                                    'registrationToken':response['response'][0]['registrationToken'] if response.get('statusCode')==1 else None,
                                    'parkingName':parkingOwnerResponse['response'][0]['parkingName'] if response.get('statusCode')==1 else None,
                                    'vehicleTypeName':mailData[0]['vehicleTypeName'],
                                    'inTime':mailData[0]['inTime']
                                    
                                    
                                }
                            })
            else:
                messagePublisher.publish(queueName='notificationService', message = {
                                'action':'vehicleOuttimemail',
                                'body':{
                                    'emailId': response['response'][0]['emailId'] if response.get('statusCode')==1 else None,
                                    'phoneNo': response['response'][0]['phoneNumber'] if response.get('statusCode')==1 else None,
                                    'userName':response['response'][0]['userName'] if response.get('statusCode')==1 else None,
                                    'userId':response['response'][0]['userId'] if response.get('statusCode')==1 else None,
                                    'registrationToken':response['response'][0]['registrationToken'] if response.get('statusCode')==1 else None,
                                    'parkingName':parkingOwnerResponse['response'][0]['parkingName'] if response.get('statusCode')==1 else None,
                                    'vehicleTypeName':mailData[0]['vehicleTypeName'],
                                    'outTime':mailData[0]['outTime']
                                    
                                }
                            })


            return 'celery working fine'
    except Exception as e:
        return str(e)
