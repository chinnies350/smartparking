from pyodbc import OperationalError
import aioodbc
from aioodbc.cursor import Cursor
from concurrent.futures import ThreadPoolExecutor
import asyncio
from fastapi import HTTPException
from fastapi import status
import redis
import celery
import os
from dotenv import load_dotenv
load_dotenv()
# mssql database config

loop = asyncio.get_event_loop()

async def get_cursor() -> Cursor:
    try:
        dsn = r'Driver={ODBC Driver 17 for SQL Server};Server={192.168.1.221};Database={smart_parking_user_service};UID={sqldeveloper};PWD={SqlDeveloper$};MARS_Connection=yes;APP=yourapp'

        async with aioodbc.connect(dsn=dsn, executor=ThreadPoolExecutor(max_workers=50), loop=loop) as conn:
            async with conn.cursor() as cur:
                yield cur
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                                detail='DB connectivity failed')

# redis database config
redis_client=redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))

# celery configuration
# celeryWorker = celery.Celery(os.getenv('CELERY_TASKNAME'), broker=f"amqp://{os.getenv('CELERY_USERNAME')}:{os.getenv('CELERY_PASSWORD')}@{os.getenv('CELERY_HOST')}:{os.getenv('CELERY_PORT')}/%2f")
celeryWorker = celery.Celery(os.getenv('CELERY_TASKNAME'), broker=f'redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}/{os.getenv("CELERY_REDIS_DB")}')