import aioodbc
from aioodbc.cursor import Cursor
from fastapi import HTTPException
from starlette import status
import asyncio
from concurrent.futures import ThreadPoolExecutor
import redis
import celery
import os
from dotenv import load_dotenv

load_dotenv()
# mssql asynchronous connection
loop = asyncio.get_event_loop()

async def get_cursor() -> Cursor:
    dsn = r'Driver={ODBC DRIVER 17 for SQL SERVER};Server={192.168.1.221};Database={smart_parking_slot_service};UID={sqldeveloper};PWD={SqlDeveloper$};MARS_Connection=yes;APP=yourapp'
    try:
        async with aioodbc.connect(dsn=dsn, loop=loop,executor=ThreadPoolExecutor(max_workers=50)) as conn:
            async with conn.cursor() as cur:
                yield cur
    except Exception as e:
        print("Exception as get_cursor",str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="DB connectivity failed")
        
        
# redis database config
redis_client=redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))
print("redis_client",redis_client)
# celery configuration
celeryWorker = celery.Celery(os.getenv('CELERY_TASKNAME'), broker=f"amqp://{os.getenv('CELERY_USERNAME')}:{os.getenv('CELERY_PASSWORD')}@{os.getenv('CELERY_HOST')}:{os.getenv('CELERY_PORT')}/%2f")


