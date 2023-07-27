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

userWalletRouter = APIRouter(prefix='/userWallet')

async def userWalletUniqueIdDetails(uniqueId,userId,status,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT * 
							FROM userWalletView
							WHERE uniqueId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(uniqueId))
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
        print("Exception as userWalletUniqueIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
async def userWalletUserIdDetails(uniqueId,userId,status,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT * 
							FROM userWalletView
							WHERE userId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(userId))
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
        print("Exception as userWalletUserIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def userWalletUserIdStatusDetails(uniqueId,userId,status,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT * 
							FROM userWalletView
							WHERE userId=? AND status=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(userId,status))
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
        print("Exception as userWalletUserIdStatusDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        
async def userWalletDetails(uniqueId,userId,status,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT * 
							FROM userWalletView
                                FOR JSON PATH) AS VARCHAR(MAX))""")
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
        print("Exception as userWalletDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

parkingPassDict = {
   
   "uniqueId=True, userId=False, status=False":userWalletUniqueIdDetails,
   "uniqueId=False, userId=True, status=False":userWalletUserIdDetails,
   "uniqueId=False, userId=True, status=True":userWalletUserIdStatusDetails,
   "uniqueId=False, userId=False, status=False":userWalletDetails
   
  
}

@userWalletRouter.get('')
async def getUserWallet(uniqueId:Optional[int]=Query(None),userId:Optional[int]=Query(None),status:Optional[date]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"uniqueId={True if uniqueId else False}, userId={True if userId else False}, status={True if status else False}"
        return await parkingPassDict[st](uniqueId, userId, status,db)
    except Exception as e:
        print("Exception as getUserWallet ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@userWalletRouter.post('')
async def postUserWallet(request:schemas.UserWallet,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postUserWallet]
                                                @userId =?,
                                                @walletAmt =?,
                                                @loyaltyPoints =?,
                                                @status=?,
                                                @expiryDate =?,
                                                @creditedDate =?,
                                                @reasonToCredit =?
                                                
                                                """,
                                            (request.userId,
                                            request.walletAmt,
                                            request.loyaltyPoints,
                                            request.status,
                                            request.expiryDate,
                                            request.creditedDate,
                                            request.reasonToCredit
                                            ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postUserWallet ",str(e))
        return{"statusCode":0,"response":"Server Error"}