from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from fastapi import Response
from aioodbc.cursor import Cursor
from routers.eventsServer import publish
import schemas
# from routers.config import engine 
from routers.config import get_cursor
from task import passlot
from typing import Optional
from fastapi import Query
import time
import json,os,ast
import routers
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/cancellationRules",tags=['cancellationRules'])


async def cancellationRulesDetailsBasedOnuniqueId(uniqueId,activestatus,diffDate,time,type,bookingId,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT crv.* FROM cancellationRulesView AS crv
                                WHERE uniqueId = ?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (uniqueId))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as cancellationRulesDetailsBasedOnuniqueId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def cancellationRulesDetailsBasedOnactivestatus(uniqueId,activestatus,diffDate,time,type,bookingId,db):

    try:
        await db.execute(f"""SELECT CAST((SELECT crv.* FROM cancellationRulesView AS crv
                                WHERE activestatus = ?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (activestatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as cancellationRulesDetailsBasedOnactivestatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def getcancellationDateTimeDetails(uniqueId,activestatus,diffDate,time,type,bookingId,db):
    try:
        await db.execute(f"""EXEC [dbo].[getCancellationRefundCharges] ?,?""",(diffDate,time))
        row = await db.fetchone()
        return {
            "response":0 if row==None else row,
            "statusCode":1
        }                
    except Exception as e:
        print("Exception as getcancellationDateTimeDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def cancellationRulesDetailsBasedOntype(uniqueId,activestatus,diffDate,time,type,bookingId,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT crv.* FROM cancellationRulesView AS crv
                                WHERE type = ?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (type))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as cancellationRulesDetailsBasedOntype ",str(e))
        return {
            "response":str(e),
            "statusCode":0
        }

async def cancellationRulesDetailsBasedOnBookingId(uniqueId,activestatus,diffDate,time,type,bookingId,db):
    try:
        data=[]
        url = f"{os.getenv('BOOKING_URL')}/booking?bookingId={bookingId}"
        response = await routers.client.get(url)
        var = json.loads(response.text)
        if var['statusCode']==1:
            for id in var['response'] :
                await db.execute(f"""SELECT CAST((SELECT (CASE 
                                                    WHEN EXISTS (SELECT * FROM (SELECT MIN(duration) as minDuration FROM cancellationRules WHERE type='D' AND DATEDIFF(day , ISNULL(('{id['createdDate']}'),'0'), GETDATE()) <= duration AND ISNULL(('{id['fromDate']}'),'0') >= GETDATE()) as subTab WHERE subTab.minDuration IS NOT NULL)
                                                            THEN 'Y'
                                                    WHEN EXISTS (SELECT * FROM (SELECT MIN(duration) as minDuration FROM cancellationRules WHERE type='M' AND duration >= (DATEDIFF(day, ISNULL(('{id['createdDate']}'),'0'), GETDATE()) * 1440 ) AND ISNULL(('{id['fromDate']}'),'0') >= GETDATE()) as subTab WHERE subTab.minDuration IS NOT NULL)
                                                        THEN 'Y'
                                                    ELSE
                                                            'N'
                                            END) AS cancellation
                                            FOR JSON PATH) AS VARCHAR(MAX))""")
                row = await db.fetchone()
                if row[0] != None:           
                    data=(json.loads(row[0]))

            if len(data) !=0:
                return {
                "response":data,
                "statusCode":1
                }
            else:                
                return {
                    "response":"data not found",
                    "statusCode":0
                }
        return {
                    "response":"data not found",
                    "statusCode":0
                }
    except Exception as e:
        print("Exception as cancellationRulesDetailsBasedOnUserId ",str(e))
        return {
            "response":str(e),
            "statusCode":0
        }



async def getcancellationRulesDetails(uniqueId,activestatus,diffDate,time,type,bookingId,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT crv.* FROM cancellationRulesView AS crv
                                FOR JSON PATH) AS VARCHAR(MAX))""")
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getcancellationRulesDetails ",str(e))
        return {
            "response":str(e),
            "statusCode":0
        }

cancellationRulesDict = {

    "uniqueId=True, activestatus=False, diffDate=False, time=False, type=False, bookingId=False":cancellationRulesDetailsBasedOnuniqueId,
    "uniqueId=False, activestatus=True, diffDate=False, time=False, type=False, bookingId=False":cancellationRulesDetailsBasedOnactivestatus,
    "uniqueId=False, activestatus=False, diffDate=True, time=True, type=False, bookingId=False":getcancellationDateTimeDetails,
    "uniqueId=False, activestatus=False, diffDate=False, time=False, type=False, bookingId=False":getcancellationRulesDetails,
    "uniqueId=False, activestatus=False, diffDate=False, time=False, type=True, bookingId=False":cancellationRulesDetailsBasedOntype,
    "uniqueId=False, activestatus=False, diffDate=False, time=False, type=False, bookingId=True":cancellationRulesDetailsBasedOnBookingId
}

@router.get('')
async def cancellationRulesGet(uniqueId:Optional[int]=Query(None),activestatus:Optional[str]=Query(None), diffDate:Optional[str]=Query(None), time:Optional[int]=Query(None), type:Optional[str]=Query(None), bookingId:Optional[int]=Query(None), db:Cursor = Depends(get_cursor)):
    try:
        st = f"uniqueId={True if uniqueId else False}, activestatus={True if activestatus else False}, diffDate={True if diffDate else False}, time={True if time else False}, type={True if type else False}, bookingId={True if bookingId else False}"
        return await cancellationRulesDict[st](uniqueId,activestatus,diffDate,time,type,bookingId,db)

    except Exception as e:
        print("Exception as cancellationRulesGet ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.post('')
async def cancellationRules(request:schemas.CancellationRules,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postCancellationRules]
                                                    @type =?,
                                                    @duration=?,
                                                    @noOfTimesPerUser =?,
                                                    @cancellationCharges=?,
                                                    @activeStatus =?,
                                                    @createdBy =?
                                                    
                                                    """,
                                                (request.type,
                                                request.duration,
                                                request.noOfTimesPerUser,
                                                request.cancellationCharges,
                                                request.activeStatus,
                                                request.createdBy
                                                ))
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
async def putcancellationRules(request:schemas.PutCancellationRules,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putCancellationRules]
                                                    @type =?,
                                                    @duration=?,
                                                    @noOfTimesPerUser =?,
                                                    @cancellationCharges=?,
                                                    @updatedBy =?,
                                                    @uniqueId=?
                                                    """,
                                                (
                                                request.type,
                                                request.duration,
                                                request.noOfTimesPerUser,
                                                request.cancellationCharges,
                                                request.updatedBy,
                                                request.uniqueId
                                                ))

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
async def deletecancellationRules(uniqueId:int,activeStatus:str,db:Cursor=Depends(get_cursor)):
    try:
        result=await db.execute(f"""UPDATE cancellationRules SET activeStatus=? WHERE uniqueId=?""",(activeStatus,uniqueId))
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
