from fastapi.routing import  APIRouter
from fastapi import Depends
from aioodbc.cursor import Cursor
from typing import Optional
from fastapi import Query
from routers.config import get_cursor
from routers import Response
import json,os 
from datetime import date
from dotenv import load_dotenv
load_dotenv()

paymentTransactionHistoryRouter = APIRouter(prefix="/paymentTransactionHistory",tags=['paymentTransactionHistory'])


@paymentTransactionHistoryRouter.get('')
async def getPaymentTransactionHistory(fromDate:Optional[date]=Query(None), toDate:Optional[date]=Query(None),paymentType:Optional[int]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[getPaymentTransactionHistory] ?,?,?""",(fromDate, toDate,paymentType))
        row = await db.fetchone()
        if row[0]:
            return {"statusCode": 1, "response":  json.loads(row[0]) if row[0] != None else []}
        else:
            return Response("NotFound")
            
    except Exception as e:
        print("Exception as getPaymentTransactionHistory ",str(e))
        return {
            'response':"Server Error",
            'statusCode': 0
        }