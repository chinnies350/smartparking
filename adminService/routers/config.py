import aioodbc
from aioodbc.cursor import Cursor
from pyodbc import OperationalError
from starlette import status
from fastapi.exceptions import HTTPException
import asyncio
from concurrent.futures import ThreadPoolExecutor
import redis
import celery
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

loop = asyncio.get_event_loop()



# client = MongoClient("103.155.12.18", 38762)
client = MongoClient("mongodb://admin:Prematix%40123@192.168.1.169:7017/?authMechanism=DEFAULT")
db = client['smart_parking']
Base_Url = "http://192.168.1.19:5020/"


async def get_cursor() -> Cursor:
    try:
        dsn = r'Driver={ODBC Driver 17 for SQL Server};Server={192.168.1.221};Database={smart_parking_admin_service};UID={sqldeveloper};PWD={SqlDeveloper$};MARS_Connection=yes;APP=yourapp'
        async with aioodbc.connect(dsn=dsn, loop=loop, executor=ThreadPoolExecutor(max_workers=50)) as conn:
            async with conn.cursor() as cur:
                yield cur

    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="DB connectivity failed")

# redis database config
redis_client=redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))

# celery configuration
# celeryWorker = celery.Celery(os.getenv('CELERY_TASKNAME'), broker=f"amqp://{os.getenv('CELERY_USERNAME')}:{os.getenv('CELERY_PASSWORD')}@{os.getenv('CELERY_HOST')}:{os.getenv('CELERY_PORT')}/%2f")

celeryWorker = celery.Celery(os.getenv('CELERY_TASKNAME'), broker=f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{os.getenv("CELERY_REDIS_DB")}')


