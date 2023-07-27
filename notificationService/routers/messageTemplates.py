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

messageTemplatesRouter = APIRouter(prefix='/messageTemplates')

@messageTemplatesRouter.get('')
async def getMessageTemplate(uniqueId:Optional[int]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[getMessageTemplates] ?""",uniqueId)
        row = await db.fetchone()
        if row[0]:
            return {"statusCode": 1, "response":  json.loads(row[0]) if row[0] != None else []}
        return { "statusCode": 0,
                    "response": "Data Not Found"}
            
    except Exception as e:
        print("Exception as getMessageTemplate ",str(e))
        return {
            'response':"Server Error",
            'statusCode': 0
        }

@messageTemplatesRouter.post('')
async def postMessageTemplate(request:schemas.PostMessageTemplates,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postMessageTemplates] 
                        @messageHeader=?,
                        @subject=?,
                        @messageBody=?,
                        @templateType=?,
                        @peid=?,
                        @tpid=?,
                        @createdBy=?
                      """,
                      (request.messageHeader,
                        request.subject,
                        request.messageBody,
                        request.templateType,
                        request.peid,
                        request.tpid,
                        request.createdBy
                                            ))
        row=await db.fetchall()
        await db.commit()
        return{"statusCode":int(row[0][1]),"response":row[0][0]}

    except Exception as e:
        print("Exception as postMessageTemplate ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@messageTemplatesRouter.put('')
async def putMessageTemplate(request:schemas.PutMessageTemplates,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putMessageTemplates] 
                               @messageHeader=?,
                               @subject=?,
                               @messageBody=?,
                               @templateType=?,
                               @peid=?,
                               @tpid=?,
                               @uniqueId=?,
                               @updatedBy=?
                               """,
                                (request.messageHeader,
                                 request.subject,
                                 request.messageBody,
                                 request.templateType,
                                 request.peid,
                                 request.tpid,
                                 request.uniqueId,
                                 request.updatedBy
                                            ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putMessageTemplate ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@messageTemplatesRouter.delete('')
async def deleteMessageTemplates(uniqueId:int,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("DELETE FROM messageTemplates WHERE uniqueId=?",uniqueId)
        await db.commit()
        if result.rowcount>=1:
            return {
                    "statusCode": 1,
                    "response": "Data Deleted Successfully"}
            
        else:
            return { "statusCode": 0,
                    "response": "Data Not Deleted"}

    except Exception as e:
        print("Exception as deleteMessageTemplate ",str(e))
        return{"stausCode":0, "response":"Server Error"}