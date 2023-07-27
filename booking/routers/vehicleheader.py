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
from routers.config import get_cursor,redis_client
# from task import passlot
import time
import json,os 
import asyncio
#from task import vehicleHeaderDetailsmail
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/vehicleHeader",tags=['vehicleHeader'])

# async def getNameDetails(vehicleType):
#     try:
#         vehicleTypeName = redis_client.hget('vehicleConfigMaster', vehicleType)
#         vehicleImageUrl = redis_client.hget('vehicleConfigMaster', vehicleType)
                
#         vehicleTypeName=vehicleTypeName.decode("utf-8") if vehicleTypeName else None
#         vehicleImageUrl=vehicleImageUrl.decode("utf-8") if vehicleImageUrl else None
#         return vehicleTypeName,vehicleImageUrl
#     except Exception as e:
#         print("Exception as getNameDetails ",str(e))
#         return {
#             "response":"Server Error",
#             "statusCode":0
#         }

async def passTransactionIdDetails(parkingPassTransId,type,branchId,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT vh.* 
                                            FROM vehicleHeader as vh 
                                            WHERE vh.bookingPassId=? AND vh.bookingIdType='P'
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
        print("Exception as vehicleHeader passTransactionIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def passTransactionIdTypeDetails(parkingPassTransId,type,branchId,db):
    try:
        
        if type=='O':
            await db.execute(f"""SELECT CAST((SELECT vh.* 
                                                FROM vehicleHeader as vh 
                                                WHERE vh.bookingPassId=? AND vh.bookingIdType='P' AND vh.vehicleStatus='I'
                                            FOR JSON PATH) AS VARCHAR(MAX))""",(parkingPassTransId))
        elif type=='I':
            await db.execute(f"""SELECT CAST((SELECT vh.* 
                                                FROM vehicleHeader as vh 
                                                WHERE vh.bookingPassId=? AND vh.bookingIdType='P' AND vh.vehicleStatus IS NULL
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
        print("Exception as passTransactionIdTypeDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def vehicleHeaderSlotIds(parkingPassTransId,type,branchId,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ISNULL((vh.slotId),0)AS slotId,vh.vehicleType 
                                            FROM vehicleHeader as vh 
                                        FOR JSON PATH) AS VARCHAR(MAX))""")
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
        print("Exception as vehicleHeader vehicleHeaderSlotIds ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getBookingDetailsBasedOnBranchId(parkingPassTransId,type,branchId,db):
    try:        
        await db.execute(f"""SELECT CAST((SELECT ISNULL(COUNT(vh.vehicleHeaderId),0) AS slotCapacity 
                                            FROM booking as b 
											INNER JOIN vehicleHeader as vh 
                                            ON b.bookingId = vh.bookingPassId AND vh.bookingIdType='B'
                                            WHERE (b.fromDate =  CONVERT(DATE, GETDATE())
                                                AND b.paidAmount > 0
                                                AND b.branchId = ?) 
                                            FOR JSON PATH) AS  varchar(max))""",(branchId))
        row = await db.fetchone()        
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as getBookingDetailsBasedOnBranchId",str(e))
        return{"statusCode":0,"response":"Server Error"}



parkingPassDict = {
   "parkingPassTransId=True, type=False, branchId=False":passTransactionIdDetails,
   "parkingPassTransId=True, type=True, branchId=False":passTransactionIdTypeDetails,
   "parkingPassTransId=False, type=False, branchId=False":vehicleHeaderSlotIds,
   "parkingPassTransId=False, type=False, branchId=True":getBookingDetailsBasedOnBranchId,
}

@router.get('')
async def getVehicleHeader(parkingPassTransId:Optional[int]=Query(None),type:Optional[str]=Query(None),branchId:Optional[int]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"parkingPassTransId={True if parkingPassTransId else False}, type={True if type else False}, branchId={True if branchId else False}"
        return await parkingPassDict[st](parkingPassTransId, type, branchId, db)
    except Exception as e:
        print("Exception as getVehicleHeader ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.post('')
async def postVehicleHeader(request:schemas.PostVehicleHeader,db:Cursor=Depends(get_cursor)):
    try:
        vehicleDetails=redis_client.hget('vehicleConfigMaster',request.vehicleType)
        vehicleTypeName,vehicleImageUrl=tuple(json.loads(vehicleDetails.decode("utf-8")).values()) if vehicleDetails else None
        await db.execute(f"""EXEC [dbo].[postVehicleHeader]
                                                    @bookingIdType=?,
                                                    @bookingPassId =?,
                                                    @vehicleType =?,
                                                    @vehicleTypeName=?,
                                                    @vehicleImageUrl=?,
                                                    @vehicleNumber =?,
                                                    @inTime =?,
                                                    @vehicleStatus =?,
                                                    @createdBy =?                      
                                                    """,
                                                (request.bookingIdType,
                                                request.bookingPassId,
                                                request.vehicleType,
                                                vehicleTypeName,
                                                vehicleImageUrl,
                                                request.vehicleNumber,
                                                request.inTime,
                                                request.vehicleStatus,
                                                request.createdBy
                                                ))
        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as postVehicleHeader ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.put('')
async def putVehicleHeader(request:schemas.PutVehicleHeader,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putVehicleHeader] ?,?,?,?,?,?,?,?,?,?,?""",
                                                (request.inTime,
                                                request.outTime,
                                                request.vehicleHeaderId,
                                                request.updatedBy,
                                                request.vehicleStatus,
                                                request.slotId,
                                                request.paidAmount,
                                                request.paymentType,
                                                request.transactionId,
                                                request.bankName,
                                                request.bankReferenceNumber))
        rows=await db.fetchall()
        if rows[0][1]==1:
            if request.inTime!=None:
                res='I'
            else:
                res='O'        
            await publish(queueName='slotManagement', message ={
                        'action':'block',
                        'body':{
                            'slotId': request.slotId,
                            'inOut':res
                        }
                        })
            vehicleHeaderDetailsmail.delay(json.loads(rows[0][2]),res)
            return{
                "statusCode":int(rows[0][1]),
                "response":rows[0][0]
            }
        else:
            return{            
                'response': 'data not updated',
                'statusCode':0
                }
    except Exception as e:
        print("Exception as putVehicleHeader ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
