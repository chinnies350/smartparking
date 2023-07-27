
from fastapi.routing import APIRouter
from fastapi import BackgroundTasks, Depends
from aioodbc.cursor import Cursor
from routers.config import get_cursor,redis_client
import json
from dotenv import load_dotenv
load_dotenv()
import routers
import os,json



router = APIRouter(prefix="/getDataBasedOnSlotId",tags=['booking'])


async def getbookingDetails(bookingPassId,slotId):
    try:
        response = await routers.client.get(f"{os.getenv('BOOKING_URL')}/booking?bookingId={bookingPassId}&slotId={slotId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            
            return response['response'][0]
        return "NULL"
    except Exception as e:
        print("Exception as getPriceTaxId ",str(e))
        return ""
    
async def getPassbookingDetails(bookingPassId,slotId):
    try:
        response = await routers.client.get(f"{os.getenv('BOOKING_URL')}/passBookingTransaction?passBookingTransactionId={bookingPassId}&slotId={slotId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            
            return response['response'][0]
        return "NULL"
    except Exception as e:
        print("Exception as getPriceTaxId ",str(e))
        return ""


@router.get("/")
async def getDataBasedOnSlotId(slotId,db:Cursor = Depends(get_cursor)):
    try:
        data = []
        await db.execute(f"""
                    SELECT TOP 1 vh.bookingIdType,vh.bookingPassId
                    FROM vehicleHeader as vh
                    INNER JOIN userSlot as us ON us.bookingPassId = vh.bookingPassId
                    WHERE (vh.vehicleStatus != 'O' OR vh.vehicleStatus IS NULL) AND us.slotId =?
                    ORDER BY vh.vehicleStatus DESC
                    """,(slotId))
        row = await db.fetchone()
        if row[0]!='NULL' and row[0]=='B' and row[1]!='NULL':
            bookingdeatils=await getbookingDetails(row[1],slotId)
        elif row[0]!='NULL' and row[0]=='P' and row[1]!='NULL':
            bookingdeatils=await getPassbookingDetails(row[1],slotId)
        
        if bookingdeatils!='NULL':

                return {
                    "response": bookingdeatils,
                    "statusCode":1
                }
        else:
            return {
                "response": "data not found",
                "statusCode": 0
            }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnbookingTypeanduserId",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
