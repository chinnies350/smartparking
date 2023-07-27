import aioodbc
import asyncio
import redis
import celery
import os
from dotenv import load_dotenv
from aioodbc.cursor import Cursor
from pyodbc import OperationalError
from fastapi import HTTPException
from fastapi import status
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

loop = asyncio.get_event_loop()

async def get_cursor() -> Cursor:
    try:
        dsn = r'Driver={ODBC Driver 17 for SQL Server};Server={192.168.1.221};Database={smart_parking_notification_service};UID={sqldeveloper};PWD={SqlDeveloper$};MARS_Connection=yes;APP=yourapp'

        async with aioodbc.connect(dsn=dsn, loop=loop, executor=ThreadPoolExecutor(max_workers=50)) as conn:
            async with conn.cursor() as cur:
                yield cur
    except OperationalError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail='DB connectivity failed')





