
import json
from producer import messagePublisher
import os
from dotenv import load_dotenv
import celery
import redis
import requests

load_dotenv()
# from routers.eventServer import publish

redis_client=redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))

celeryWorker = celery.Celery(os.getenv('CELERY_TASKNAME'), broker=f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{os.getenv("CELERY_REDIS_DB")}')

@celeryWorker.task()
def userSubscription(userId):
    print("userSubscription called",userId)
   
    url=f"{os.getenv('USER_SERVICE_URL')}/userMaster?userId={userId}"
    response = requests.get(url)
    response = json.loads(response.text)
    if response['statusCode'] == 1:
        messagePublisher.publish(queueName='notificationService', message = {
                        'action':'Subscription',
                        'body':{
                            'emailId': response['response'][0]['emailId'],
                            'phoneNo': response['response'][0]['phoneNumber'],
                            'userName':response['response'][0]['userName']
                            
                        }
                    })
    return 'celery working fine'


