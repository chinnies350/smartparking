import aioodbc
from aioodbc.cursor import Cursor
from fastapi import HTTPException
from starlette import status
import asyncio
from pyodbc import OperationalError
from concurrent.futures import ThreadPoolExecutor
import redis
import celery
import os
from dotenv import load_dotenv
load_dotenv()

# mssql asynchronous connection
loop = asyncio.get_event_loop()

async def get_cursor() -> Cursor:
    dsn = r'Driver={ODBC Driver 17 for SQL Server};Server={192.168.1.221};Database={smart_parking_pass_module};UID={sqldeveloper};PWD={SqlDeveloper$};MARS_Connection=yes;APP=yourapp'
    try:
        async with aioodbc.connect(dsn=dsn, loop=loop, executor=ThreadPoolExecutor(max_workers=50)) as conn:
            async with conn.cursor() as cur:
                yield cur
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail="DB connectivity failed")


# redis database configuration
# cacheClient = redis.Redis(host='192.168.1.17', port=6379, db=0)

redis_client=redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))
# celery configuration
celeryWorker = celery.Celery('task', broker="amqp://admin:Prematix%40123@192.168.1.17:5672/%2f")
