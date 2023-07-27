# from routers.config import celeryWorker,redis_client
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
def postConfigName(id,value):
    print("postConfigName called",id,value)
    try:
        redis_client.hset('configMaster', id, value)
        return 'celery working fine'
    except Exception as e:
        return str(e)

@celeryWorker.task()
def postTaxName(id,value):
    print("postTaxName called",id,value)
    try:
        redis_client.hset('taxMaster', id, value)
        return 'celery working fine'
    except Exception as e:
        return str(e)


@celeryWorker.task()
def postVehicleName(id,value,imgUrl,vehiclePlaceHolderImageUrl):
    print("postVehicleName called",id,value,imgUrl,vehiclePlaceHolderImageUrl)
    try:
        redis_client.hmset('vehicleConfigMaster',{str(id):json.dumps({'vehicleTypeName':value,'vehicleImageUrl':imgUrl,'vehiclePlaceHolderImageUrl':vehiclePlaceHolderImageUrl})})
        return 'celery working fine'
    except Exception as e:
        return str(e)
    



@celeryWorker.task()
def postChargePinConfigName(id,value,imgUrl):
    print("postChargePinConfigName called",id,value,imgUrl)
    try:
        redis_client.hmset('chargePinConfigMaster',{str(id):json.dumps({'chargePinConfig':value,'chargePinImageUrl':imgUrl})})
    except Exception as e:
        return str(e)

