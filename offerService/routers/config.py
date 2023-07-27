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

load_dotenv()

loop = asyncio.get_event_loop()

async def get_cursor() -> Cursor:
    try:
        dsn = r'Driver={ODBC Driver 17 for SQL Server};Server={192.168.1.221};Database={smart_parking_offer_module};UID={sqldeveloper};PWD={SqlDeveloper$};MARS_Connection=yes;APP=yourapp'
        async with aioodbc.connect(dsn=dsn, loop=loop, executor=ThreadPoolExecutor(max_workers=50)) as conn:
            async with conn.cursor() as cur:
                yield cur

    except OperationalError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail="DB connectivity failed")

# redis database config
redis_client=redis.Redis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'), db=os.getenv('REDIS_DB'))
print("redis_client",redis_client)
# celery configuration
celeryWorker = celery.Celery(os.getenv('CELERY_TASKNAME'), broker=f"amqp://{os.getenv('CELERY_USERNAME')}:{os.getenv('CELERY_PASSWORD')}@{os.getenv('CELERY_HOST')}:{os.getenv('CELERY_PORT')}/%2f")




