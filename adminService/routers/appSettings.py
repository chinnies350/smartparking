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

appSettingsRouter = APIRouter(prefix='/appSettings')

@appSettingsRouter.get('')
async def getAppSettings(uniqueId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None), appVersion:Optional[int]=Query(None),appType:Optional[str]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[getAppSettings] ?,?,?,?""",(uniqueId,activeStatus,appVersion,appType))
        row = await db.fetchone()
        if row[0]:
            return {"statusCode": 1, "response":  json.loads(row[0]) if row[0] != None else []}
        return { "statusCode": 0,
                    "response": "Data Not Found"}
            
    except Exception as e:
        print("Exception as getAppSettings ",str(e))
        return {
            'response':"Server Error",
            'statusCode': 0
        }

@appSettingsRouter.post('')
async def postAppSettings(request:schemas.AppSettings,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postAppSettings]
                                                @privacyPolicy =?,
                                                @termsAndConditions =?,
                                                @appVersion =?,
                                                @appType=?,
                                                @activeStatus=?,
                                                @createdBy =?
                                                
                                                """,
                                            (request.privacyPolicy,
                                            request.termsAndConditions,
                                            request.appVersion,
                                            request.appType,
                                            request.activeStatus,
                                            request.createdBy
                                            ))
        row=await db.fetchall()
        await db.commit()
        return{"statusCode":int(row[0][1]),"response":row[0][0]}

    except Exception as e:
        print("Exception as postAppSettings ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@appSettingsRouter.put('')
async def putAppSettings(request:schemas.PutAppSettings,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putappSettings]
                                                @privacyPolicy =?,
                                                @termsAndConditions =?,
                                                @appVersion =?,
                                                @appType=?,
                                                @updatedBy =?,
                                                @uniqueId=?
                                                """,
                                            (
                                            request.privacyPolicy,
                                            request.termsAndConditions,
                                            request.appVersion,
                                            request.appType,
                                            request.updatedBy,
                                            request.uniqueId
                                            ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putAppSettings ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@appSettingsRouter.delete('')
async def deleteAppSettings(uniqueId:int,activeStatus:str,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE appSettings SET activeStatus=? WHERE uniqueId=?",activeStatus,uniqueId)
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
        print("Exception as deleteAppSettings ",str(e))
        return{"stausCode":0, "response":"Server Error"}