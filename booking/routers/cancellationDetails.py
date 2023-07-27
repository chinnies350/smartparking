import json
from sqlite3 import Cursor
import routers
from fastapi.routing import APIRouter
from routers.config import get_cursor
from fastapi import Depends
from typing import Optional
from fastapi import Query
import schemas
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

cancellationDetailsRouter = APIRouter(prefix='/cancellationDetails')


async def getBookingIdDetails(bookingId,db):
    try:
        await db.execute(f"""
                            SELECT CAST((SELECT DATEDIFF(DAY, createdDate, GETDATE()) AS diffDay, 
                                                DATEDIFF(MINUTE , createdDate, GETDATE()) AS time
                                        FROM booking
                                        WHERE bookingId = ?
                            FOR JSON PATH) as VARCHAR(max))
                        """, (bookingId))
        
        row = await db.fetchone()
        if row[0] != None:
            return json.loads(row[0])[0]
        return {}
    except Exception as e:
        print("Exception as getBookingIdDetails ",str(e))
        return ""



async def getDetailsBasedOnbookingId(bookingId, db):
    try:
        getBookingDetails=await getBookingIdDetails(bookingId,db)
        response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/cancellationRules?diffDate={getBookingDetails.get('diffDay')}&time={getBookingDetails.get('time')}")
        response = json.loads(response.text)
        await db.execute(f"""
                            SELECT CAST((SELECT totalAmount, paidAmount, {response['response']} AS cancellationCharge, ISNULL(paidAmount,0) - ISNULL({response['response']},0) AS refundAmount
                                            FROM booking
                                            WHERE bookingId = ?
                            FOR JSON PATH) as VARCHAR(max))
                        """, (bookingId))
        row = await db.fetchone()
        if row[0] != None:
            return {"statusCode":1,"response":json.loads(row[0])}
        else:
           return {"statusCode":0,"response":"Data Not Found"} 
    
    except Exception as e:
        print("Exception as getDetailsBasedOnbookingId ",str(e))
        return {
            'response':"Server Error",
            'statusCode': 0
        }
@cancellationDetailsRouter.get('')
async def getCancellation(bookingId: int, db: Cursor = Depends(get_cursor)):
    try:
        if bookingId:
            return await getDetailsBasedOnbookingId(bookingId, db)
            
    except Exception as e:
        print("Exception as getCancellation ",str(e))
        return {
            'response':"Server Error",
            'statusCode': 0
        }

@cancellationDetailsRouter.put('')
async def putCancellation(request:schemas.CancellationUpdate,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f""""EXEC [dbo].[putCancellation]
                                    @refundStatus=?,
                                    @cancellationCharges=?,
                                    @cancellationReason=?,
                                    @updatedBy=?,
                                    @bookingId=?""",
                                    (request.refundStatus,
                                    request.cancellationCharges,
                                    request.cancellationReason,
                                    request.updatedBy,
                                    request.bookingId))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putCancellation ",str(e))
        return{"statusCode":0,"response":"Server Error"}