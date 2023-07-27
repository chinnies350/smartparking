import json
from sqlite3 import Cursor
import routers
from fastapi.routing import APIRouter
from fastapi import Depends
from typing import Optional
from fastapi import Query
import schemas
from routers.config import get_cursor
import os
import asyncio
from routers.eventServer import publish
from dotenv import load_dotenv
from datetime import date,time

load_dotenv()

parkingOwnerConfigRouter = APIRouter(prefix='/parkingOwnerConfig')

@parkingOwnerConfigRouter.get('')
async def getParkingOwnerConfig(parkingOwnerId:Optional[int]=Query(None),branchId:Optional[int]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[getParkingOwnerConfig] ?,?""",(parkingOwnerId,branchId))
        row = await db.fetchone()
        if row[0]:
            return {"statusCode": 1, "response":  json.loads(row[0]) if row[0] != None else []}
        return{"statusCode": 0, "response":"Data Not Found"}
    except Exception as e:
        print("Exception as getMenuOptions ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@parkingOwnerConfigRouter.post('')
async def postParkingOwnerConfig(request:schemas.PostParkingOwnerConfig,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postParkingOwnerConfig]
                                        @parkingOwnerId =?,
										@branchId =?,
                                        @blockOption=?,
                                        @floorOption=?,
                                        @squareFeet= ?,
										@floorType=?,
                                        @employeeOption =?,
                                        @slotsOption=?,
                                        @createdBy =?
                                                
                                                """,
                                            (request.parkingOwnerId,
                                            request.branchId,
                                            request.blockOption,
                                            request.floorOption,
                                            request.squareFeet,
                                            request.floorType,
                                            request.employeeOption,
                                            request.slotsOption,
                                            request.createdBy
                                            ))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            if request.blockOption=='N':
                await publish(queueName="parkingOwnerService", message={
                                                    'action':'postBlockMaster',
                                                    'body':{
                                                        "parkingOwnerId" :request.parkingOwnerId,
                                                        "branchId": request.branchId ,
                                                        "blockName" :'A-Block',
                                                        "activeStatus":'A' ,
                                                        "approvalStatus" :'A',
                                                        "createdBy":request.createdBy,
                                                        "floorOption":request.floorOption,
                                                        "squareFeet":request.squareFeet,
                                                        "floorType":request.floorType,
                                                        "floorName":int(row[2])
                                                        
                                                    }
                                                    })
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postMenuOptions ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@parkingOwnerConfigRouter.put('')
async def putParkingOwnerConfig(request:schemas.PutParkingOwnerConfig,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putParkingOwnerConfig]
                                                @parkingOwnerConfigId=?,
                                                @parkingOwnerId =?,
                                                @branchId =?,
                                                @blockOption=?,
                                                @floorOption =?,
                                                @squareFeet= ?,
										        @floorType=?,
                                                @employeeOption =?,
                                                @slotsOption=?,
                                                @updatedBy= ?
                                                
                                                """,
                                            (request.parkingOwnerConfigId,
                                            request.parkingOwnerId,
                                            request.branchId,
                                            request.blockOption,
                                            request.floorOption,
                                            request.squareFeet,
                                            request.floorType,
                                            request.employeeOption,
                                            request.slotsOption,
                                            request.updatedBy
                                            ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putMenuOptions ",str(e))
        return{"statusCode":0,"response":"Server Error"}


