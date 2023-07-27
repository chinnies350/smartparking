import json
from sqlite3 import Cursor
import routers
from fastapi.routing import APIRouter
from fastapi import Depends
from typing import Optional
from fastapi import Query
import schemas
from routers.config import get_cursor,redis_client
import os
import asyncio
from dotenv import load_dotenv
from datetime import date,time

load_dotenv()

feedBackRouter = APIRouter(prefix='/feedBackMaster')

async def getNameDetails(parkingOwnerId,branchId):
    try:
        parkingName = redis_client.hget('parkingOwnerMaster', parkingOwnerId)
        branchName = redis_client.hget('branchMaster', branchId)
        parkingName=parkingName.decode("utf-8") if parkingName else None
        branchName=branchName.decode("utf-8") if branchName else None
        return parkingName,branchName
    except Exception as e:
        print("Exception as getNameDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
    
async def feedBackIdDetails(FeedbackId, parkingOwnerId, branchId, bookingId,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT fm.*,um.userName 
							FROM feedBackMaster AS fm
                            INNER JOIN userMaster as um
                            ON um.userId=fm.createdBy
							WHERE FeedbackId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(FeedbackId))
        row = await db.fetchone()
        
        if row[0] != None:
            return {
                "response":json.loads(row[0]),
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as feedBackIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
async def feedBackParkingOwnerIdDetails(FeedbackId, parkingOwnerId, branchId, bookingId,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT fm.*,um.userName 
							FROM feedBackMaster AS fm
                            INNER JOIN userMaster as um
                            ON um.userId=fm.createdBy
							WHERE parkingOwnerId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(parkingOwnerId))
        row = await db.fetchone()
        
        if row[0] != None:
            return {
                "response":json.loads(row[0]),
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as feedBackParkingOwnerIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def feedBackParkingOwnerFeedbackIdDetails(FeedbackId, parkingOwnerId, branchId, bookingId,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT fm.*,um.userName 
							FROM feedBackMaster AS fm
                            INNER JOIN userMaster as um
                            ON um.userId=fm.createdBy
							WHERE parkingOwnerId=? AND FeedbackId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(parkingOwnerId,FeedbackId))
        row = await db.fetchone()
        
        if row[0] != None:
            return {
                "response":json.loads(row[0]),
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as feedBackParkingOwnerFeedbackIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
async def feedBackBranchIdDetails(FeedbackId, parkingOwnerId, branchId, bookingId,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT fm.*,um.userName 
							FROM feedBackMaster AS fm
                            INNER JOIN userMaster as um
                            ON um.userId=fm.createdBy
							WHERE branchId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(branchId))
        row = await db.fetchone()
        
        if row[0] != None:
            
            return {
                "response":json.loads(row[0]),
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as feedBackBranchIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def feedBackBookingIdDetails(FeedbackId, parkingOwnerId, branchId, bookingId,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT fm.*,um.userName 
							FROM feedBackMaster AS fm
                            INNER JOIN userMaster as um
                            ON um.userId=fm.createdBy
							WHERE bookingId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(bookingId))
        row = await db.fetchone()
        
        if row[0] != None:
            return {
                "response":json.loads(row[0]),
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as feedBackBookingIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def feedBackDetails(FeedbackId, parkingOwnerId, branchId, bookingId,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT fm.*,um.userName
							FROM feedBackMaster AS fm
                            INNER JOIN userMaster as um
                            ON um.userId=fm.createdBy
                                FOR JSON PATH) AS VARCHAR(MAX))""")
        row = await db.fetchone()
        
        if row[0] != None:
            
            return {
                "response":json.loads(row[0]),
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as feedBackDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

parkingPassDict = {
   
   "FeedbackId=True, parkingOwnerId=False, branchId=False, bookingId=False":feedBackIdDetails,
   "FeedbackId=False, parkingOwnerId=True, branchId=False, bookingId=False":feedBackParkingOwnerIdDetails,
   "FeedbackId=True, parkingOwnerId=True, branchId=False, bookingId=False":feedBackParkingOwnerFeedbackIdDetails,
   "FeedbackId=False, parkingOwnerId=False, branchId=True, bookingId=False":feedBackBranchIdDetails,
   "FeedbackId=False, parkingOwnerId=False, branchId=False, bookingId=True":feedBackBookingIdDetails,
   "FeedbackId=False, parkingOwnerId=False, branchId=False, bookingId=False":feedBackDetails
  
}

@feedBackRouter.get('')
async def getFeedBack(FeedbackId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),bookingId:Optional[int]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"FeedbackId={True if FeedbackId else False}, parkingOwnerId={True if parkingOwnerId else False}, branchId={True if branchId else False}, bookingId={True if bookingId else False}"
        return await parkingPassDict[st](FeedbackId, parkingOwnerId, branchId, bookingId,db)
    except Exception as e:
        print("Exception as getFeedBack ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@feedBackRouter.post('')
async def postFeedBack(request:schemas.FeedBackMaster,db:Cursor = Depends(get_cursor)):
    try:
        parkingName,branchName=await getNameDetails(request.parkingOwnerId,
                                request.branchId)
        await db.execute(f"""EXEC [dbo].[postFeedBackMaster]
                                    @parkingOwnerId=?,
                                    @parkingName=?,
                                    @branchId=?,
                                    @branchName=?,
                                    @bookingId=?,
                                    @feedbackRating=?,
                                    @feedbackComment=?,
                                    @createdBy=?""",
                                (request.parkingOwnerId,
                                parkingName,
                                request.branchId,
                                branchName,
                                request.bookingId,
                                request.feedbackRating,
                                request.feedbackComment,
                                request.createdBy
                                ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postFeedBack ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@feedBackRouter.put('')
async def putFeedBack(request:schemas.PutFeedBackMaster,db:Cursor = Depends(get_cursor)):
    try:
        parkingName,branchName=await getNameDetails(request.parkingOwnerId,
                                request.branchId)
        await db.execute(f"""EXEC [dbo].[putFeedBackMaster]
                                    @feedbackRating=?,
                                    @feedbackComment=?,
                                    @updatedBy=?,
                                    @FeedbackId=?,
                                    @parkingOwnerId=?,
                                    @parkingName=?,
                                    @branchId=?,
                                    @branchName=?,
                                    @bookingId=?""",
                                (request.feedbackRating,
                                request.feedbackComment,
                                request.updatedBy,
                                request.FeedbackId,
                                request.parkingOwnerId,
                                parkingName,
                                request.branchId,
                                branchName,
                                request.bookingId
                                ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putFeedBack ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@feedBackRouter.delete('')
async def deleteFeedBack(FeedbackId:int,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute("DELETE FROM feedBackMaster WHERE FeedbackId=?",FeedbackId)
        await db.commit()
        if db.rowcount>=1:
            return {
                         "statusCode": 1,
                         "response": "Deleted Successfully"}
        else:
            return { "statusCode": 0,
                    "response": "Data Not Found"}

    except Exception as e:
        print("Exception as deleteFeedBack ",str(e))
        return{"statusCode":0,"response":"Server Error"}