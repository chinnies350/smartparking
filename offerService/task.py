import os
from dotenv import load_dotenv
import celery
import redis
import json

load_dotenv()

# redis database config
redis_client=redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))

# celery configuration
celeryWorker = celery.Celery(os.getenv('CELERY_TASKNAME'), broker=f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{os.getenv("CELERY_REDIS_DB")}')


@celeryWorker.task()
def postOfferName(id,value,offerDescription):
    print("postOfferName called",id,value,offerDescription)
    try:
        redis_client.hmset('offerMaster',{str(id):json.dumps({'offerName':value,'offerDescription':offerDescription})})
    except Exception as e:
        return str(e)