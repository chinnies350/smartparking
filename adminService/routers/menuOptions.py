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
from dotenv import load_dotenv
from datetime import date,time

load_dotenv()

menuOptionsRouter = APIRouter(prefix='/menuOptions')

async def getDetailsBasedOnOptionId(optionId,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT * 
							FROM menuOptions
							WHERE optionId=? FOR JSON PATH) AS  varchar(max))""", (optionId))
        row = await db.fetchone()
        if row[0] != None:
            data=json.loads(row[0])
            return {
                "statusCode":1,
                "response": data
                
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnOptionId ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
async def getDetailsBasedOnActiveStatus(activeStatus,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT * 
							FROM menuOptions
							WHERE activeStatus=? FOR JSON PATH) AS  varchar(max))""", (activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            data=json.loads(row[0])
            return {
                "statusCode":1,
                "response": data
                
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnActiveStatus ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
async def getMenuOptionsDetails(db):
    try:
        await db.execute(f"""SELECT CAST((SELECT * 
							FROM menuOptions
							 FOR JSON PATH) AS  varchar(max))""")
        row = await db.fetchone()
        if row[0] != None:
            data=json.loads(row[0])
            return {
                "statusCode":1,
                "response": data
                
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as getMenuOptionsDetails ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@menuOptionsRouter.get('')
async def getMenuOptions(optionId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        if optionId:
            return await getDetailsBasedOnOptionId(optionId, db)
        elif activeStatus:
            return await getDetailsBasedOnActiveStatus(activeStatus, db)
        else:
            return await getMenuOptionsDetails(db)
    except Exception as e:
        print("Exception as getMenuOptions ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@menuOptionsRouter.post('')
async def postMenuOptions(request:schemas.MenuOptions,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postMenuOption]
                                                @parkingOwnerId=?,
                                                @moduleId=?,
                                                @optionName=?,
                                                @activeStatus=?,
								                @createdBy=?
                                                """,
                        (
                            request.parkingOwnerId,
                            request.moduleId,
                            request.optionName,
                            request.activeStatus,
                            request.createdBy  
                        ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postMenuOptions ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@menuOptionsRouter.put('')
async def putMenuOptions(request:schemas.PutMenuOptions,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putMenuOption]
                                                @parkingOwnerId=?,
                                                @moduleId=?,
                                                @optionName=?,
                                                @activeStatus=?,
								                @updatedBy=?,
                                                @optionId=?
                                                """,
                        (
                            request.parkingOwnerId,
                            request.moduleId,
                            request.optionName,
                            request.activeStatus,
                            request.updatedBy,
                            request.optionId
                        ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putMenuOptions ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@menuOptionsRouter.delete('')
async def deleteMenuOptions(activeStatus:str,optionId:int,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE menuOptions SET activeStatus=? WHERE optionId=?",activeStatus,optionId)
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
        print("Exception as deleteMenuOptions ",str(e))
        return{"statusCode":0,"response":"Server Error"}