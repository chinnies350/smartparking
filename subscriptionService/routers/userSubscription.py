import json
from sqlite3 import Cursor
import routers
from fastapi.routing import APIRouter
from routers.config import get_cursor,redis_client
from fastapi import Depends
from typing import Optional
from fastapi import Query
import schemas
import os
import asyncio
from dotenv import load_dotenv
from task import userSubscription

load_dotenv()

userSubscriptionRouter = APIRouter(prefix='/userSubscription')

async def getNameDetails(taxId,userId):
    try:
        taxName = redis_client.hget('taxMaster', taxId)
        userName = redis_client.hget('userMaster', userId)
        taxName=taxName.decode("utf-8") if taxName else None
        userName=userName.decode("utf-8") if userName else None
        return taxName,userName
    except Exception as e:
        print("Exception as getNameDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        } 

async def getDetailsBasedOnId(subscriptionId,userId,taxId, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT usm.*,sm.subscriptionName
                                                FROM userSubscription AS usm
                                                INNER JOIN subscriptionMaster as sm
                                                ON usm.subscriptionId=sm.subscriptionId
                                                WHERE usm.subscriptionId = ? AND userId=? AND taxId=? FOR JSON PATH) AS  varchar(max))""", (subscriptionId,userId,taxId))
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
        print("Exception as getDetailsBasedOnId ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def getDetailsBasedOnSubscriptionId(subscriptionId, db):
    try:
       
        await db.execute(f"""SELECT CAST((SELECT usm.*,sm.subscriptionName
                                                FROM userSubscription AS usm
                                                INNER JOIN subscriptionMaster as sm
                                                ON usm.subscriptionId=sm.subscriptionId
                                                WHERE usm.subscriptionId = ? FOR JSON PATH) AS  varchar(max))""", (subscriptionId))
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
        print("Exception as getDetailsBasedOnSubscriptionId ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def getDetailsBasedOnPassId(passId, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT usm.*,sm.subscriptionName
                                                FROM userSubscription AS usm
                                                INNER JOIN subscriptionMaster as sm
                                                ON usm.subscriptionId=sm.subscriptionId
                                                WHERE usm.passId = ? FOR JSON PATH) AS  varchar(max))""", (passId))
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
        print("Exception as getDetailsBasedOnPassId ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def getDetailsBasedOnUserId(userId, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT usm.*,sm.subscriptionName
                                                FROM userSubscription AS usm
                                                INNER JOIN subscriptionMaster as sm
                                                ON usm.subscriptionId=sm.subscriptionId
                                                WHERE usm.userId = ? FOR JSON PATH) AS  varchar(max))""", (userId))
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
        print("Exception as getDetailsBasedOnUserId ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def getDetailsBasedOnTaxId(taxId, db):
    try:
        await db.execute(f"""SELECT CAST(MAX(usm.createdDate) as date)AS userSubscription
                                FROM userSubscription AS usm
                                WHERE usm.taxId = ?
                                """, (taxId))
        row = await db.fetchone()
        if row[0] != None:           
            return {
            "response":row[0],
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnTaxId ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }


async def getUserSubscriptionDetails(db):
    try:
        await db.execute(f"""SELECT CAST((SELECT usm.*,sm.subscriptionName
                                                    FROM userSubscription AS usm
                                                    INNER JOIN subscriptionMaster as sm
                                                    ON usm.subscriptionId=sm.subscriptionId  FOR JSON PATH) AS  varchar(max))""")
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
        print("Exception as getUserSubscriptionDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

@userSubscriptionRouter.get('')
async def getUserSubscriptionMaster(passId:Optional[int]=Query(None),userId:Optional[int]=Query(None),subscriptionId:Optional[int]=Query(None),taxId:Optional[int]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        if subscriptionId and userId and taxId:
            return await getDetailsBasedOnId(subscriptionId,userId,taxId, db)
        elif subscriptionId:
            return await getDetailsBasedOnSubscriptionId(subscriptionId, db)
        elif passId:
            return await getDetailsBasedOnPassId(passId, db)
        elif userId:
            return await getDetailsBasedOnUserId(userId, db)
        elif taxId:
            return await getDetailsBasedOnTaxId(taxId, db)
        else:
            return await getUserSubscriptionDetails(db)
    except Exception as e:
        print("Exception as getUserSubscriptionMaster ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }


@userSubscriptionRouter.post('')
async def postUserSubscriptionMaster(request:schemas.UserSubscription,db:Cursor = Depends(get_cursor)):
    try:
        taxName,userName=await getNameDetails(request.taxId,request.userId)
        await db.execute(f"""EXEC [dbo].[postUserSubscription]
                                    @userId=?,
                                    @userName=?,
                                    @subscriptionId=?,
                                    @validityFrom=?,
                                    @validityTo=?,
                                    @actualCount=?,
                                    @remainingCount=?,
                                    @taxId=?,
                                    @taxName=?,
                                    @amount=?,
                                    @tax=?,
                                    @totalAmount=?,
                                    @passType=?
                                    
                                    """,
                                (request.userId,
                                userName,
                                request.subscriptionId,
                                request.validityFrom,
                                request.validityTo,
                                request.actualCount,
                                request.remainingCount,
                                request.taxId,
                                taxName,
                                request.amount,
                                request.tax,
                                request.totalAmount,
                                request.passType
                               
                                ))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            userSubscription.delay(request.userId)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postUserSubscriptionMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@userSubscriptionRouter.put('')
async def putUserSubscriptionMaster(request:schemas.PutUserSubscription,db:Cursor = Depends(get_cursor)):
    try:
        taxName,userName=await getNameDetails(request.taxId,request.userId)
        await db.execute(f"""EXEC [dbo].[putUserSubscription]
                                    @validityFrom=?,
                                    @validityTo=?,
                                    @actualCount=?,
                                    @remainingCount=?,
                                    @amount=?,
                                    @tax=?,
                                    @totalAmount=?,
                                    @passType=?,
                                    @passId=?,
                                    @userId=?,
                                    @userName=?,
                                    @subscriptionId=?,
                                    @taxId=?,
                                    @taxName=?""",
                                (
                                request.validityFrom,
                                request.validityTo,
                                request.actualCount,
                                request.remainingCount,
                                request.amount,
                                request.tax,
                                request.totalAmount,
                                request.passType,
                                request.passId,
                                request.userId,
                                userName,
                                request.subscriptionId,
                                request.taxId,
                                taxName))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putUserSubscriptionMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}



@userSubscriptionRouter.delete('')
async def deleteUserSubscriptionMaster(passId:int,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("DELETE FROM userSubscription WHERE passId=?",passId)
        await db.commit()
        if result.rowcount>=1:
            return {
                    "statusCode": 1,
                    "response": "Data Deleted Successfully"}
            
        else:
            return { "statusCode": 0,
                    "response": "Data Not Deleted"}

    except Exception as e:
        print("Exception as deleteUserSubscriptionMaster ",str(e))
        return{"stausCode":0, "response":"Server Error"}