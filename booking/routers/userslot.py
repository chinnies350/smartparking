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
import time
import json,os 
import asyncio
from dotenv import load_dotenv
load_dotenv()

router=APIRouter(prefix='/userSlot',tags=["userSlot"])

async def passTransactionIdDetails(parkingPassTransId,activeStatus,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT us.* 
                                            FROM userSlot as us 
                                            WHERE us.bookingPassId=? AND us.bookingIdType='P'
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
        print("Exception as userSlot passTransactionIdDetails",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getBookingDetailsBasedOnActiveStatus(parkingPassTransId,activeStatus,db):
    try:
        url1=f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/branchMaster?activeStatus={activeStatus}"
        response = await routers.client.get(url1)
        var1 = json.loads(response.text)
        if var1['statusCode']==1:
            for id in var1['response']:        
                await db.execute(f"""SELECT CAST((SELECT branchId, us.slotId 
                                                    FROM booking as b
                                                    INNER JOIN userSlot as us 
                                                    ON us.bookingPassId = b.bookingId AND us.bookingIdType = 'B'
                                                    WHERE (b.fromDate =  CONVERT(DATE, GETDATE()))
                                                    AND b.branchId = {id['branchId']}
                                                    AND b.paidAmount > 0
                                                    GROUP BY branchId, us.slotId
                                                    FOR JSON AUTO,INCLUDE_NULL_VALUES) AS  varchar(max))""")
                row = await db.fetchone()
                if row[0] != None:           
                    data=(json.loads(row[0]))

            return {
                "response": data,
                "statusCode":1
            }

        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as getBookingDetailsBasedOnActiveStatus",str(e))
        return{"statusCode":0,"response":"Server Error"}


parkingPassDict = {
   "parkingPassTransId=True,activeStatus=False":passTransactionIdDetails,
   "parkingPassTransId=False,activeStatus=True":getBookingDetailsBasedOnActiveStatus
}

@router.get('')
async def getUserSlot(parkingPassTransId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"parkingPassTransId={True if parkingPassTransId else False},activeStatus={True if activeStatus else False}"
        return await parkingPassDict[st](parkingPassTransId,activeStatus,db)
    except Exception as e:
        print("Exception as getUserSlot ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.put('')
async def putUserSlot(userSlotId:int,slotId:int,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putUserSlot] ?,?""",(userSlotId,slotId))
        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as putUserSlot ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }