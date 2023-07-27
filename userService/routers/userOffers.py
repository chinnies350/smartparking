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
from task import userOffersData
load_dotenv()

useroffersRouter = APIRouter(prefix='/userOffers')

async def userOffersUserIdDetails(offerId,fromDate, toDate, userId,userOfferId,type,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT uf.userId,uf.offerId,uf.fromDate,uf.toDate,uf.fromTime,uf.toTime,um.userName
                                FROM userOffers as uf
                                INNER JOIN userMaster as um
                                ON um.userId=uf.userId
                                WHERE uf.userId=? AND uf.activeStatus='A' 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(userId))
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
        print("Exception as userOffersUserIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def userOffersUserOffersIdDetails(offerId,fromDate, toDate, userId,userOfferId,type,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT uf.* 
                                FROM userOffers as uf
                                WHERE uf.userOfferId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(userOfferId))
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
        print("Exception as userOffersUserOffersIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def userOffersOfferIdDetails(offerId,fromDate, toDate, userId,userOfferId,type,db):
    try:
        
        
        await db.execute(f"""SELECT CAST((SELECT uf.* 
                                FROM userOffers as uf
                                WHERE uf.offerId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(offerId))
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
        print("Exception as userOffersOfferIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def userOffersFromDateDetails(offerId,fromDate, toDate, userId,userOfferId,type,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT uf.* 
                                FROM userOffers as uf
                                WHERE uf.fromDate=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(fromDate))
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
        print("Exception as userOffersFromDateDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def userOffersToDateDetails(offerId,fromDate, toDate, userId,userOfferId,type,db):
    try:
        
        
        await db.execute(f"""SELECT CAST((SELECT uf.* 
                                FROM userOffers as uf
                                WHERE uf.toDate=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(toDate))
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
        print("Exception as userOffersToDateDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def userOffersOfferIdDateDetails(offerId,fromDate, toDate, userId,userOfferId,type,db):
    try:
        
        
        await db.execute(f"""SELECT CAST((SELECT uf.* 
                                FROM userOffers as uf
                                WHERE uf.toDate=? AND uf.fromDate=? AND uf.userOfferId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(toDate,fromDate,userOfferId))
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
        print("Exception as userOffersOfferIdDateDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def userOffersTypeDetails(offerId,fromDate, toDate, userId,userOfferId,type,db):
    try:
        
        if type=='R':
            await db.execute(f"""SELECT CAST((SELECT * FROM (SELECT usv.*
                                                ,DATEDIFF(day,CAST(GETDATE() AS date),usv.toDate)AS remainingCount
                                                FROM userOffers AS usv
                                                WHERE usv.userId=?)as subtab WHERE remainingCount>0  FOR JSON PATH) AS  varchar(max))""", (userId))
        elif type=='E':
            await db.execute(f"""SELECT CAST((SELECT usv.*
					                            FROM userOffers AS usv
					                            WHERE userId=? AND DATEDIFF(day,CAST(GETDATE() AS date),usv.toDate)=1  FOR JSON PATH) AS  varchar(max))""", (userId))
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
        print("Exception as userOffersTypeDetails ",str(e))
        return {
            "statusCode": 0,
            "response": str(e)
            
        }
async def userOffersDetails(offerId,fromDate, toDate, userId,userOfferId,type,db):
    try:
        
        
        await db.execute(f"""SELECT CAST((SELECT uf.* 
                                FROM userOffers as uf
                               
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
        print("Exception as userOffersDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

parkingPassDict = {
   
   "offerId=False, fromDate=False, toDate=False, userId=True, userOfferId=False, type=False":userOffersUserIdDetails,
   "offerId=False, fromDate=False, toDate=False, userId=False, userOfferId=True, type=False":userOffersUserOffersIdDetails,
   "offerId=True, fromDate=False, toDate=False, userId=False, userOfferId=False, type=False":userOffersOfferIdDetails,
   "offerId=False, fromDate=True, toDate=False, userId=False, userOfferId=False, type=False":userOffersFromDateDetails,
   "offerId=False, fromDate=False, toDate=True, userId=False, userOfferId=False, type=False":userOffersToDateDetails,
   "offerId=False, fromDate=True, toDate=True, userId=False, userOfferId=True, type=False":userOffersOfferIdDateDetails,
   "offerId=False, fromDate=False, toDate=False, userId=True, userOfferId=False, type=True":userOffersTypeDetails,
   "offerId=False, fromDate=False, toDate=False, userId=False, userOfferId=False, type=False":userOffersDetails
  
}

@useroffersRouter.get('')
async def getUserOffers(offerId:Optional[int]=Query(None),fromDate:Optional[date]=Query(None),toDate:Optional[date]=Query(None),userId:Optional[int]=Query(None),userOfferId:Optional[int]=Query(None),type:Optional[str]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"offerId={True if offerId else False}, fromDate={True if fromDate else False}, toDate={True if toDate else False}, userId={True if userId else False}, userOfferId={True if userOfferId else False}, type={True if type else False}"
        return await parkingPassDict[st](offerId, fromDate, toDate, userId, userOfferId, type, db)
    except Exception as e:
        print("Exception as getUserOffers ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@useroffersRouter.post('')
async def postUserOffers(request:schemas.UserOffers,db:Cursor = Depends(get_cursor)):
    try:
        offerDetails=redis_client.hget('offerMaster',request.offerId)
        offerName,offerDescription=tuple(json.loads(offerDetails.decode("utf-8")).values()) if offerDetails else None
        await db.execute(f"""EXEC [dbo].[postUserOffers]
                                    @userId=?,
                                    @offerId=?,
                                    @offerName=?,
                                    @offerDescription=?,
                                    @fromDate=?,
                                    @toDate=?,
                                    @fromTime=?,
                                    @toTime=?,
                                    @activeStatus=?""",
                                    (request.userId,
                                    request.offerId,
                                    offerName,
                                    offerDescription,
                                    request.fromDate,
                                    request.toDate,
                                    request.fromTime,
                                    request.toTime,
                                    request.activeStatus))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            userOffersData.delay(json.loads(row[2]),request.offerId,request.userId)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}
    except Exception as e:
        print("Exception as postUserOffers ",str(e))
        return{"statusCode":0,"response":"Server Error"}