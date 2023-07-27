import json
from sqlite3 import Cursor
from fastapi.routing import APIRouter
from routers.config import get_cursor
from fastapi import Depends
from typing import Optional
from fastapi import Query
import schemas
import os
import routers
from task import postChargePinConfigName

chargePinConfigRouter = APIRouter(prefix='/chargePinConfig')

@chargePinConfigRouter.get('')
async def getChargePinConfig(chargePinId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[getchargePinConfig] ?,?""",(chargePinId,activeStatus))
        row = await db.fetchone()
        if row[0]:
            return {"statusCode": 1, "response":  json.loads(row[0]) if row[0] != None else []}
        return { "statusCode": 0,
                    "response": "Data Not Found"}
            
    except Exception as e:
        print("Exception as getChargePinConfig ",str(e))
        return {
            'response':"Server Error",
            'statusCode': 0
        }

@chargePinConfigRouter.post('')
async def postChargePinConfig(request:schemas.ChargePinConfig,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postChargePinConfig]
                                    @chargePinConfig=?,
                                    @chargePinImageUrl=?,
                                    @activeStatus=?,
                                    @createdBy=?""",
                        (
                            request.chargePinConfig,
                            request.chargePinImageUrl,
                            request.activeStatus,
                            request.createdBy
                                            ))
        row=await db.fetchall()
        await db.commit()
        if int(row[0][1])==1:
            print(row)
            postChargePinConfigName.delay(int(row[0][2]),request.chargePinConfig,request.chargePinImageUrl)
            return{"statusCode":int(row[0][1]),"response":row[0][0]}
        return{"statusCode":int(row[0][1]),"response":row[0][0]}

    except Exception as e:
        print("Exception as postChargePinConfig ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@chargePinConfigRouter.put('')
async def putChargePinConfig(request:schemas.PutChargePinConfig,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putChargePinConfig]
                                    @chargePinConfig=?,
                                    @chargePinImageUrl=?,
                                    @updatedBy=?,
                                    @chargePinId=?""",
                        (
                            request.chargePinConfig,
                            request.chargePinImageUrl,
                            request.updatedBy,
                            request.chargePinId
                                            ))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            postChargePinConfigName.delay(request.chargePinId,request.chargePinConfig,request.chargePinImageUrl)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putChargePinConfig ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@chargePinConfigRouter.delete('')
async def deleteChargePinConfig(chargePinId:int,activeStatus:str,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE chargePinConfig SET activeStatus=? WHERE chargePinId=?",activeStatus,chargePinId)
        await db.commit()
        if result.rowcount>=1:
            if activeStatus=='D':
                return {
                         "statusCode": 1,
                         "response": "Deactivated successfully"}
            else:
                return {"statusCode": 1,
                        "response": "Activated successfully"}
        else:
            return { "statusCode": 0,
                    "response": "Data Not Found"}

    except Exception as e:
        print("Exception as deleteChargePinConfig ",str(e))
        return{"stausCode":0, "response":"Server Error"}