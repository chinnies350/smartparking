
from fastapi.routing import APIRouter
from fastapi import BackgroundTasks, Depends
from aioodbc.cursor import Cursor
from routers.config import get_cursor,redis_client
import json
from dotenv import load_dotenv
load_dotenv()
import routers
import os,json



router = APIRouter(prefix="/getDataBasedOnVehicleNumberAndPhone",tags=['booking'])


async def getpassId(phoneNumber):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?type=A&phoneNumber={phoneNumber}")
        response = json.loads(response.text)
        return response['response'][0]['parkingPassTransId'] if response['statusCode'] == 1 else 'NULL'
        
    except Exception as e:
        print("Exception as getpassId ",str(e))
        return 0
    
    
async def getbookingDetails(bookingPassId):
    try:
        response = await routers.client.get(f"{os.getenv('BOOKING_URL')}/booking?bookingId={bookingPassId}&Type='A'")
        return json.loads(response.text)
    except Exception as e:
        print("Exception as getbookingDetails ",str(e))
        return ""
    
async def getPassbookingDetails(bookingPassId):
    try:
        response = await routers.client.get(f"{os.getenv('BOOKING_URL')}/passBookingTransaction?passBookingTransactionId={bookingPassId}&type=A")
        return json.loads(response.text)
       
    except Exception as e:
        print("Exception as getPassbookingDetails ",str(e))
        return ""


@router.get("/")
async def getDataBasedOnVehicleNumberAndPhone(inOutDetails,floorId,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""
                    DECLARE @bookingIdType CHAR(1),
                    @bookingPassId INT,
                    @tempVar VARCHAR(10),
                    @inOutDetails NVARCHAR(15)='{inOutDetails}',
                    @floorId INT={floorId};

                    BEGIN TRY

                        SELECT TOP 1 @bookingIdType = mainData.bookingIdType, @bookingPassId = mainData.bookingPassId
                        FROM (SELECT vh.vehicleHeaderId, vh.bookingIdType, vh.bookingPassId, vh.vehicleStatus 
                        FROM booking as b
                        INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId AND vh.bookingIdType = 'B'
                        WHERE (vh.vehicleStatus != 'O' OR vh.vehicleStatus IS NULL) 
                        AND b.phoneNumber = @inOutDetails
                        AND b.floorId = @floorId
                        UNION
                        SELECT vh.vehicleHeaderId, vh.bookingIdType, vh.bookingPassId, vh.vehicleStatus
                        FROM passBookingTransaction as pbt
                        INNER JOIN vehicleHeader as vh ON vh.bookingPassId = pbt.passBookingTransactionId AND vh.bookingIdType = 'P'
                        WHERE (vh.vehicleStatus != 'O' OR vh.vehicleStatus IS NULL) 
                        AND pbt.floorId = @floorId
                        AND pbt.passTransactionId='{await getpassId(inOutDetails)}'
                        ) as mainData
                        ORDER BY mainData.vehicleStatus DESC

                    END TRY

                    BEGIN CATCH
                        SELECT TOP 1 @bookingIdType = mainData.bookingIdType, @bookingPassId = mainData.bookingPassId
                        FROM (SELECT vh.vehicleHeaderId, vh.bookingIdType, vh.bookingPassId, vh.vehicleStatus 
                        FROM booking as b
                        INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId AND vh.bookingIdType = 'B'
                        WHERE (vh.vehicleStatus != 'O' OR vh.vehicleStatus IS NULL) 
                        AND vh.vehicleNumber = @inOutDetails
                        AND b.floorId =@floorId
                        UNION
                        SELECT vh.vehicleHeaderId, vh.bookingIdType, vh.bookingPassId, vh.vehicleStatus 
                        FROM passBookingTransaction as pbt
                        INNER JOIN vehicleHeader as vh ON vh.bookingPassId = pbt.passBookingTransactionId AND vh.bookingIdType = 'P'
                        WHERE (vh.vehicleStatus != 'O' OR vh.vehicleStatus IS NULL) 
                        AND vh.vehicleNumber =@inOutDetails
                        AND pbt.floorId = @floorId
                        ) as mainData
                        ORDER BY mainData.vehicleStatus DESC
                    END CATCH

                    select @bookingIdType,@bookingPassId
                    """)
        row = await db.fetchone()
        if row[0] !=None:  
            if row[0]=='B':
                bookingdeatils=await getbookingDetails(row[1])
            elif row[0]=='P':
                bookingdeatils=await getPassbookingDetails(row[1])
            return bookingdeatils
            
        else:
            return {"response": "data not found","statusCode": 0}
    except Exception as e:
        print("Exception as getDataBasedOnVehicleNumberAndPhone",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
