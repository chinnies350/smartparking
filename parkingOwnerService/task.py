import os
from dotenv import load_dotenv
import celery
import redis

load_dotenv()

# redis database config
redis_client=redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))

# celery configuration
celeryWorker = celery.Celery(os.getenv('CELERY_TASKNAME'), broker=f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{os.getenv("CELERY_REDIS_DB")}')

@celeryWorker.task()
def passlot(queueName, message):
    return 'celery working fine'
    # eventServerProducer.publish(queueName, json.loads(message))

@celeryWorker.task()
def postParkingName(id,value):
    try:
        print("postParkingName called",id, value)
        redis_client.hset('parkingOwnerMaster', id, value)
        return 'celery working fine'
    except Exception as e:
        return str(e)

@celeryWorker.task()
def postBranchName(id,value):
    try:
        print("postBranchName called",id, value)
        redis_client.hset('branchMaster', id, value)
        return 'celery working fine'
    except Exception as e:
        return str(e)

@celeryWorker.task()
def postBlockName(id,value):
    try:
        print("postBlockName called",id, value)
        redis_client.hset('blockMaster', id, value)
        return 'celery working fine'
    except Exception as e:
        return str(e)

