from tkinter import NO
from fastapi import Query
from fastapi.routing import APIRouter
from typing import Optional
from routers.config import get_cursor
from fastapi import Depends
from aioodbc.cursor import Cursor
import json
import schemas
from dotenv import load_dotenv
load_dotenv()

configTypeRouter = APIRouter(prefix='/configType',tags=['configTypeMaster'])

async def getDetailsBasedOnConfigTypeId(configTypeId, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ca.* 
                                                FROM ConfigType AS ca  
                                                Where ca.configTypeId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (configTypeId))
        row = await db.fetchone()
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
        print("Exception as getDetailsBasedOnConfigTypeId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def configDetailsBasedOnActiveStatus(activeStatus,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ca.* 
                                            FROM ConfigType AS ca  
                                            Where ca.activeStatus=?
                            FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus))
        row = await db.fetchone()
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
        print("Exception as configDetailsBasedOnActiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def configDetailsBasedOnTypeName(typeName,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ca.* 
                                            FROM ConfigType AS ca
                                            WHERE typeName=? 
                            FOR JSON PATH) AS VARCHAR(MAX))""",(typeName))
        row = await db.fetchone()
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
        print("Exception as configDetailsBasedOnTypeName ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }



async def getConfigTypeDetails(db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ca.* FROM ConfigType AS ca
                            FOR JSON PATH) AS varchar(max))""")
        row = await db.fetchone()
        if row[0] !=None:
            return {
                "response": json.loads(row[0]),
                "statusCode":1
            }
        
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getConfigTypeDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@configTypeRouter.get('')
async def getconfigType(configTypeId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),typeName:Optional[str]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        if configTypeId:
            return await getDetailsBasedOnConfigTypeId(configTypeId,db)
        elif activeStatus:
            return await configDetailsBasedOnActiveStatus(activeStatus,db)
        elif typeName:
            return await configDetailsBasedOnTypeName(typeName,db)
        else:
            return await getConfigTypeDetails(db)
    except Exception as e:
        print("Exception as getconfigType ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@configTypeRouter.post('')
async def postConfigType(request:schemas.ConfigType,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postConfigType]
                                    @typeName=?,
                                    @activeStatus=?,
                                    @createdBy=?""",
                                (                           
                                    request.typeName,
                                    request.activeStatus,
                                    request.createdBy  
                        ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postConfigType ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@configTypeRouter.put('')
async def putConfigType(request:schemas.PutConfigType,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putConfigType]
                                    @typeName=?,
                                    @activeStatus=?,
                                    @updatedBy=?,
                                    @configTypeId=?""",
                                                                
                                    (request.typeName,
                                    request.activeStatus,
                                    request.updatedBy,
                                    request.configTypeId
                        ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putConfigType ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@configTypeRouter.delete('')
async def deleteConfigType(activeStatus:str,configTypeId:int,db:Cursor = Depends(get_cursor)):
    try:
        if activeStatus == 'A':
            await db.execute("SELECT * FROM configType WHERE typeName=(SELECT typeName FROM configType WHERE configTypeId=?) AND activeStatus = 'A' AND configTypeId != ?", (configTypeId, configTypeId))
            row = await db.fetchone()
            if row != None:
                return {
                    'statusCode': 0,
                    'response': 'Data Already Exists'
                }
        result=await db.execute("UPDATE ConfigType SET activeStatus=? WHERE configTypeId=?",activeStatus,configTypeId)
        await db.commit()
        if result.rowcount>=1:
            if activeStatus=='D':
                return {
                         "statusCode": 1,
                         "response": "Deactivated Successfully"}
            else:
                return {"statusCode": 1,
                        "response": "Activated Successfully"}
        else:
            return { "statusCode": 0,
                    "response": "Data Not Found"}

    except Exception as e:
        print("Exception as deleteConfigType ",str(e))
        return{"statusCode":0,"response":"Server Error"}

