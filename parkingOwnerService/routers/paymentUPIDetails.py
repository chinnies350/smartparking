from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from aioodbc.cursor import Cursor
from routers.eventsServer import publish
import schemas,os,routers
from typing import Optional
from fastapi import Query
# from routers.config import engine 
from routers.config import get_cursor
from routers import Response
from task import passlot
import time
import json,os 
import asyncio
from task import postBlockName
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/paymentUPIDetails",tags=['paymentUPIDetails'])


@router.get('')
async def getpaymentUPIDetails(paymentUPIDetailsId:Optional[int]=Query(None), branchId:Optional[int]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[getPaymentUPIDetails] ?,?""",(paymentUPIDetailsId, branchId))
        row = await db.fetchone()
        if row[0]:
            return {"statusCode": 1, "response":  json.loads(row[0]) if row[0] != None else []}
        else:
            return Response("NotFound")
            
    except Exception as e:
        print("Exception as getpaymentUPIDetails ",str(e))
        return {
            'response':"Server Error",
            'statusCode': 0
        }

@router.post('')
async def paymentUPIDetails(request:schemas.PaymentUPIDetails,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postPaymentUPIDetails]
                                                @name =?,
                                                @phoneNumber =?,
                                                @UPIId =?,
                                                @branchId =?,
                                                @merchantId =?,
                                                @merchantCode=?,
                                                @mode=?,
                                                @orgId=?,
                                                @sign=?,
                                                @url=?,
                                                @activeStatus =?,
                                                @createdBy =?
                                                
                                                """,
                                            (request.name,
                                            request.phoneNumber,
                                            request.UPIId,
                                            request.branchId,
                                            request.merchantId,
                                            request.merchantCode,
                                            request.mode,
                                            request.orgId,
                                            request.sign,
                                            request.url,
                                            request.activeStatus,
                                            request.createdBy
                                            )
                                            )
        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as cancellationRules ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.put('')
async def putpaymentUPIDetails(request:schemas.PutPaymentUPIDetails,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putPaymentUPIDetails]
                                                @name =?,
                                                @phoneNumber =?,
                                                @UPIId =?,
                                                @branchId =?,
                                                @merchantId =?,
                                                @merchantCode=?,
                                                @mode=?,
                                                @orgId=?,
                                                @sign=?,
                                                @url=?,
                                                @updatedBy= ?,
                                                @paymentUPIDetailsId=?
                                                
                                                """,
                                            (request.name,
                                            request.phoneNumber,
                                            request.UPIId,
                                            request.branchId,
                                            request.merchantId,
                                            request.merchantCode,
                                            request.mode,
                                            request.orgId,
                                            request.sign,
                                            request.url,
                                            request.updatedBy,
                                            request.paymentUPIDetailsId
                                            )
                                            )

        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as putcancellationRules ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.delete('')
async def deletepaymentUPIDetails(paymentUPIDetailsId:int,activeStatus:str,db:Cursor=Depends(get_cursor)):
    try:
        result=await db.execute(f"""UPDATE paymentUPIDetails SET activestatus=? Where paymentUPIDetailsId=?""",(activeStatus,paymentUPIDetailsId))
        await db.commit()
        if result.rowcount>=1:
            if activeStatus=="D":
                return{
            "statusCode": 1,
            "response": "Deactivated Successfully"
        }
            else:
                return{
            "statusCode": 1,
            "response": "Activated Successfully"
        }
        else:
            return {
            "statusCode": 0,
            "response": "Data Not Deleted"}
    except Exception as e:
        print("Exception as deletecancellationRules ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }        