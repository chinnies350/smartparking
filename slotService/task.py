# from routers.config import celeryWorker,redis_client
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
def postFloorName(id,value):
    print("postFloorName called",id,value)
    try:
        redis_client.hset('floorMaster', id, value)
    except Exception as e:
        return str(e)

# @celeryWorker.task()
# def postTaxName(id,value):
#     print("postTaxName called",id,value)
#     try:
#         redis_client.hset('taxMaster', id, value)
#     except Exception as e:
#         return str(e)
