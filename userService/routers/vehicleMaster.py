from fastapi import APIRouter
import schemas
from routers.config import get_cursor,redis_client
from fastapi import Depends
from aioodbc.cursor import Cursor
from routers import Response
from typing import Optional
import json
import routers
import os
from dotenv import load_dotenv
from fastapi import Query

load_dotenv()

vehicleMasterRouter = APIRouter(prefix='/vehicleMaster',tags=['vehicleMaster'])

async def getVehicleDetailsBasedOnUserId(userId, db):
    try:
        await db.execute(f"""
                            SELECT CAST((SELECT vmv.*
                                    FROM vehicleMasterView AS vmv
                                WHERE userId=? FOR JSON PATH) AS VARCHAR(MAX))
        """,(userId))

        row = await db.fetchone()

        if row[0] != None:
            return {
                'statusCode':1,
                'response': json.loads(row[0])
            }
        return {
            'statusCode':0,
            'response': 'Data Not Found'
        }
    except Exception as e:
        print("Exception as getVehicleDetailsBasedOnUserId ",str(e))
        return {
            'statusCode':0,
            'response':"Server Error"
        }

async def getVehicleDetailsBasedOnVehicleId(vehicleId, db):
    try:
        await db.execute(f"""
                            SELECT CAST((SELECT vmv.*
                                        FROM vehicleMasterView AS vmv
                                    WHERE vmv.vehicleId=? FOR JSON PATH) AS VARCHAR(MAX))
        """, (vehicleId))
        row = await db.fetchone()
        if row[0] != None:
           
            return {
                'statusCode':1,
                'response': json.loads(row[0])
            }
        return {
            'statusCode':0,
            'response': 'Data Not Found'
        }
    except Exception as e:
        print("Exception as getVehicleDetailsBasedOnVehicleId ",str(e))
        return {
            'statusCode':0,
            'response':"Server Error"
        }

async def getVehicleDetailsBasedOnPhoneNumber(phoneNumber, db):
    try:
        await db.execute(f"""
                            SELECT CAST((SELECT vmv.*
                                        FROM vehicleMasterView AS vmv
                                        INNER JOIN userMaster as um ON um.userId = vmv.userId
							            WHERE um.phoneNumber=?
                                     FOR JSON PATH) AS VARCHAR(MAX))
        """, (phoneNumber))
        row = await db.fetchone()
        if row[0] != None:
           
            return {
                'statusCode':1,
                'response': json.loads(row[0])
            }
        return {
            'statusCode':0,
            'response': 'Data Not Found'
        }
    except Exception as e:
        print("Exception as getVehicleDetailsBasedOnPhoneNumber ",str(e))
        return {
            'statusCode':0,
            'response':"Server Error"
        }

async def getVehicleDetailsBasedOnVehicleUserId(vehicleType,userId, db):
    try:
        await db.execute(f"""
                            SELECT CAST((SELECT vmv.*
                                        FROM vehicleMasterView AS vmv
                                    WHERE vmv.vehicleType=? AND vmv.userId=? FOR JSON PATH) AS VARCHAR(MAX))
        """, (vehicleType,userId))
        row = await db.fetchone()
        if row[0] != None:
           
            return {
                'statusCode':1,
                'response': json.loads(row[0])
            }
        return {
            'statusCode':0,
            'response': 'Data Not Found'
        }
    except Exception as e:
        print("Exception as getVehicleDetailsBasedOnVehicleUserId ",str(e))
        return {
            'statusCode':0,
            'response':"Server Error"
        }

async def getAllVehicleDetails(db):
    try:
        await db.execute(f"""
                            SELECT CAST((SELECT vmv.*
                                    FROM vehicleMasterView AS vmv
                                 FOR JSON PATH) AS VARCHAR(MAX))
        """)

        row = await db.fetchone()

        if row[0] != None:
            return {
                'statusCode':1,
                'response': json.loads(row[0])
            }
        return {
            'statusCode':0,
            'response': 'Data Not Found'
        }
    except Exception as e:
        print("Exception as getAllVehicleDetails ",str(e))
        return {
            'statusCode':0,
            'response':"Server Error"
        }

@vehicleMasterRouter.get('')
async def getVehicleDetails(userId: Optional[int]=Query(None), vehicleId: Optional[int]=Query(None), vehicleType: Optional[int]=Query(None), phoneNumber: Optional[str]=Query(None), db:Cursor = Depends(get_cursor)):
    try:
        if userId and vehicleType==None:
            return await getVehicleDetailsBasedOnUserId(userId, db)
        elif vehicleId:
            return await getVehicleDetailsBasedOnVehicleId(vehicleId, db)
        elif vehicleType and userId:
            return await getVehicleDetailsBasedOnVehicleUserId(vehicleType,userId, db)
        elif phoneNumber:
            return await getVehicleDetailsBasedOnPhoneNumber(phoneNumber, db)
        else:
            return await getAllVehicleDetails(db)
        
    except Exception as e:
        print("Exception as getVehicleDetails ",str(e))
        return {"statusCode":0,"response":"Server Error"}


@vehicleMasterRouter.post('')
async def postvehicleMaster(request:schemas.vehicleMaster, db: Cursor = Depends(get_cursor)):
    try:
        # with engine.connect() as cur:
        vehicleDetails=redis_client.hget('vehicleConfigMaster',request.vehicleType)
        vehicleTypeName,vehicleImageUrl=tuple(json.loads(vehicleDetails.decode("utf-8")).values()) if vehicleDetails else None
        await db.execute(f"""EXEC [dbo].[postVehicleMaster]
                                @userId=?,
                                @vehicleName=?,
                                @vehicleNumber=?,
                                @vehicleType=?,
                                @vehicleImageUrl=?,
                                @documentImageUrl=?,
                                @isEV=?,
                                @chargePinType=?,
                                @vehicleTypeName=?,
                                @vehicleTypeImageUrl=?
                                """,
                            (request.userId,
                            request.vehicleName,
                            request.vehicleNumber,
                            request.vehicleType,
                            request.vehicleImageUrl,
                            request.documentImageUrl,
                            request.isEV,
                            request.chargePinType,
                            vehicleTypeName,
                            vehicleImageUrl
                            ))

        row= await db.fetchone()
        await db.commit()
        return {"statusCode": int(row[1]), "response": row[0]}

    except Exception as e:
        print("Exception as postvehicleMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@vehicleMasterRouter.put('')
async def putvehicleMaster(request:schemas.PutvehicleMaster, db: Cursor = Depends(get_cursor)):
    try:
        # with engine.connect() as cur:
        vehicleDetails=redis_client.hget('vehicleConfigMaster',request.vehicleType)
        vehicleTypeName,vehicleImageUrl=tuple(json.loads(vehicleDetails.decode("utf-8")).values()) if vehicleDetails else None
        await db.execute(f"""EXEC [dbo].[putVehicleMaster]
                                @vehicleName=?,
                                @vehicleNumber=?,
                                @vehicleType=?,
                                @vehicleImageUrl=?,
                                @documentImageUrl=?,
                                @isEV=?,
                                @chargePinType=?,
                                @vehicleId=?,
                                @vehicleTypeName=?,
                                @vehicleTypeImageUrl=?,
                                @userId=?""",
                        (request.vehicleName,
                        request.vehicleNumber,
                        request.vehicleType,
                        request.vehicleImageUrl,
                        request.documentImageUrl,
                        request.isEV,
                        request.chargePinType,
                        request.vehicleId,
                        vehicleTypeName,
                        vehicleImageUrl,
                        request.userId))

        row=await db.fetchone()
        await db.commit()
        return {"statusCode": int(row[1]), "response": row[0]}


    except Exception as e:
        print("Exception as putvehicleMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@vehicleMasterRouter.delete('')
async def deletevehicleMaster(vehicleId:int, db: Cursor = Depends(get_cursor)):
    try:
        # with engine.connect() as cur:
        await db.execute("DELETE FROM vehicleMaster WHERE vehicleId=?",vehicleId)
        await db.close()
        if db.rowcount>=1:
            return Response("deleteMsg")
        else:
            return Response("NotDelete")
                
    except Exception as e:
        print("Exception as deletevehicleMaster ",str(e))
        return {"statusCode":0,"response":"Server Error"}


