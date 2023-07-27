from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from fastapi import Response
from aioodbc.cursor import Cursor
from eventsServer import publish
import schemas
import routers
from typing import Optional
from fastapi import Query
# from routers.config import engine 
from routers.config import get_cursor
# from task import passlot
import time
import json,os 
import asyncio
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/extraFees",tags=['extraFees'])

async def passTransactionIdDetails(parkingPassTransId,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ex.* 
                                            FROM extraFees as ex 
                                            WHERE ex.bookingPassId=? AND ex.bookingIdType='P'
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(parkingPassTransId))
        row = await db.fetchone()
        data=[]
        if row[0] != None:
            data=json.loads(row[0])
            return {
                "response":data,
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as ExtraFees passTransactionIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }



parkingPassDict = {
   "parkingPassTransId=True":passTransactionIdDetails
}
   

@router.get('')
async def getExtraFees(parkingPassTransId:Optional[int]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"parkingPassTransId={True if parkingPassTransId else False}"
        return await parkingPassDict[st](parkingPassTransId,db)
    except Exception as e:
        print("Exception as getExtraFees ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.post('')
async def postExtraFees(request:schemas.PostExtraFees,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postExtraFees]
                                        @bookingPassId =?,
                                        @bookingIdType=?,
                                        @count=?,
                                        @extraFee =?,
                                        @extraFeesDetails =?,
                                        @createdBy =?
                                        
                                        """,
                                        (request.bookingPassId,
                                        request.bookingIdType,
                                        request.count,
                                        request.extraFee,
                                        request.extraFeesDetails,
                                        request.createdBy
                                        ))
        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as postExtraFees ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }