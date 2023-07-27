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
from joblib import Parallel, delayed
from datetime import date,time
from task import postOfferName

load_dotenv()

offerRouter = APIRouter(prefix='/offerMaster')


def callFunction(i):
    return i.dict()



  
async def getOfferId(userId):
    try:
        
        response = await routers.client.get(f"{os.getenv('USER_SERVICE_URL')}/userOffers?userId={userId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getOfferId ",str(e))
        return ""

async def offerUserBranchIdAmountDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        data=[]
        offerId=await getOfferId(userId)
        for offer in offerId:
        
            await db.execute(f"""SELECT CAST((SELECT ofm.*,ofp.branchId,ofp.branchName,(SELECT * FROM offerRules AS ofr WHERE ofr.offerId=ofm.offerId FOR JSON PATH)AS offerRulesDetails
                                                FROM  offerMaster as ofm
                                                INNER JOIN offerMapping as ofp
                                                ON ofp.offerId=ofm.offerId 
                                                WHERE ofm.activeStatus='A' AND ofp.activeStatus='A' AND ofm.offerId=? AND (? BETWEEN minAmt AND maxAmt) AND ofp.branchId=? AND
                                                (CAST(ofm.fromDate as date) BETWEEN CAST(? as date) AND CAST(? as date) AND CAST(ofm.toDate as date) BETWEEN CAST(? as date) AND CAST(? as date)
                                                OR CAST(ofm.fromTime as time) BETWEEN CAST(? as time) AND CAST (? as time) AND CAST(ofm.toTime as time) BETWEEN CAST(? as time) AND CAST (? as time))
                                    FOR JSON PATH) AS VARCHAR(MAX))""",(offer['offerId'],Amount,branchId,offer['fromDate'],offer['toDate'],offer['fromDate'],offer['toDate'],offer['fromTime'],offer['toTime'],offer['fromTime'],offer['toTime']))
            row = await db.fetchone()
            
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    dic['userId']=offer['userId']
                    dic['userName']=offer['userName']                  
                    data.append(dic)
        
        if len(data)!=0:
            return {
                "response":data,
                "statusCode":1
            }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as offerUserBranchIdAmountDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def offerUserBranchIdAmountDateDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        data=[]
        offerId=await getOfferId(userId)
        for offer in offerId:
            await db.execute(f"""SELECT CAST((SELECT ofm.*,ofp.branchId,ofp.branchName,(SELECT * FROM offerRules AS ofr WHERE ofr.offerId=ofm.offerId FOR JSON PATH)AS offerRulesDetails
                                                FROM  offerMaster as ofm
                                                INNER JOIN offerMapping as ofp
                                                ON ofp.offerId=ofm.offerId 
                                                WHERE ofm.activeStatus='A' AND ofp.activeStatus='A' AND ofm.offerId=? AND (? BETWEEN minAmt AND maxAmt) AND ofp.branchId=? AND ofm.fromDate=? AND ofm.toDate=? AND
                                                (CAST(ofm.fromDate as date) BETWEEN CAST(? as date) AND CAST(? as date) AND CAST(ofm.toDate as date) BETWEEN CAST(? as date) AND CAST(? as date)
                                                OR CAST(ofm.fromTime as time) BETWEEN CAST(? as time) AND CAST (? as time) AND CAST(ofm.toTime as time) BETWEEN CAST(? as time) AND CAST (? as time))
                                    FOR JSON PATH) AS VARCHAR(MAX))""",(offer['offerId'],Amount,branchId,fromDate,toDate,offer['fromDate'],offer['toDate'],offer['fromDate'],offer['toDate'],offer['fromTime'],offer['toTime'],offer['fromTime'],offer['toTime']))
            row = await db.fetchone()
            
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    dic['userId']=offer['userId']
                    dic['userName']=offer['userName']                   
                    data.append(dic)
        
        if len(data)!=0:
            return {
                "response":data,
                "statusCode":1
            }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
        
    except Exception as e:
        print("Exception as offerUserBranchIdAmountDateDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def offerUserBranchIdAmountTimeDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        data=[]
        offerId=await getOfferId(userId)
        for offer in offerId:
           
            await db.execute(f"""SELECT CAST((SELECT ofm.*,ofp.branchId,ofp.branchName,(SELECT * FROM offerRules AS ofr WHERE ofr.offerId=ofm.offerId FOR JSON PATH)AS offerRulesDetails
                                                FROM  offerMaster as ofm
                                                INNER JOIN offerMapping as ofp
                                                ON ofp.offerId=ofm.offerId 
                                                WHERE ofm.activeStatus='A' AND ofp.activeStatus='A' AND ofm.offerId=? AND (? BETWEEN minAmt AND maxAmt) AND ofp.branchId=? AND ofm.fromTime=? AND ofm.toTime=? AND
                                                (CAST(ofm.fromDate as date) BETWEEN CAST(? as date) AND CAST(? as date) AND CAST(ofm.toDate as date) BETWEEN CAST(? as date) AND CAST(? as date)
                                                OR CAST(ofm.fromTime as time) BETWEEN CAST(? as time) AND CAST (? as time) AND CAST(ofm.toTime as time) BETWEEN CAST(? as time) AND CAST (? as time))
                                    FOR JSON PATH) AS VARCHAR(MAX))""",(offer['offerId'],Amount,branchId,fromTime,toTime,offer['fromDate'],offer['toDate'],offer['fromDate'],offer['toDate'],offer['fromTime'],offer['toTime'],offer['fromTime'],offer['toTime']))
            row = await db.fetchone()
            
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    dic['userId']=offer['userId']
                    dic['userName']=offer['userName']                   
                    data.append(dic)
        
        if len(data)!=0:
            return {
                "response":data,
                "statusCode":1
            }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
        
    except Exception as e:
        print("Exception as offerUserBranchIdAmountTimeDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def offerUserBranchIdAmountDateTimeDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        data=[]
        offerId=await getOfferId(userId)
        for offer in offerId:
            
            await db.execute(f"""SELECT CAST((SELECT ofm.*,ofp.branchId,ofp.branchName,(SELECT * FROM offerRules AS ofr WHERE ofr.offerId=ofm.offerId FOR JSON PATH)AS offerRulesDetails
                                                FROM  offerMaster as ofm
                                                INNER JOIN offerMapping as ofp
                                                ON ofp.offerId=ofm.offerId 
                                                WHERE ofm.activeStatus='A' AND ofp.activeStatus='A' AND ofm.offerId=? AND (? BETWEEN minAmt AND maxAmt) AND ofp.branchId=? AND ofm.fromTime=? AND ofm.toTime=? AND ofm.fromDate=? AND ofm.toDate=? AND
                                                (CAST(ofm.fromDate as date) BETWEEN CAST(? as date) AND CAST(? as date) AND CAST(ofm.toDate as date) BETWEEN CAST(? as date) AND CAST(? as date)
                                                OR CAST(ofm.fromTime as time) BETWEEN CAST(? as time) AND CAST (? as time) AND CAST(ofm.toTime as time) BETWEEN CAST(? as time) AND CAST (? as time))
                                    FOR JSON PATH) AS VARCHAR(MAX))""",(offer['offerId'],Amount,branchId,fromTime,toTime,fromDate,toDate,offer['fromDate'],offer['toDate'],offer['fromDate'],offer['toDate'],offer['fromTime'],offer['toTime'],offer['fromTime'],offer['toTime']))
            row = await db.fetchone()
            
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    dic['userId']=offer['userId']
                    dic['userName']=offer['userName']
                                       
                    data.append(dic)
        
        if len(data)!=0:
            return {
                "response":data,
                "statusCode":1
            }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
        
    except Exception as e:
        print("Exception as offerUserBranchIdAmountDateTimeDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def offerIdDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ofm.*,(SELECT * FROM offerRules AS ofr WHERE ofr.offerId=ofm.offerId FOR JSON PATH)AS offerRulesDetails 
                                        FROM offerMaster AS ofm
                                        WHERE ofm.offerId=?
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
        print("Exception as offerIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def offerUserIdDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        data=[]
        offerId=await getOfferId(userId)
        for offer in offerId:
        
            await db.execute(f"""SELECT CAST((SELECT ofm.*,ofp.branchId,ofp.branchName,(SELECT * FROM offerRules AS ofr WHERE ofr.offerId=ofm.offerId FOR JSON PATH)AS offerRulesDetails
                                                FROM  offerMaster as ofm
                                                INNER JOIN offerMapping as ofp
                                                ON ofp.offerId=ofm.offerId 
                                                WHERE ofm.activeStatus='A' AND ofp.activeStatus='A' AND ofm.offerId=? AND
                                                (CAST(ofm.fromDate as date) BETWEEN CAST(? as date) AND CAST(? as date) AND CAST(ofm.toDate as date) BETWEEN CAST(? as date) AND CAST(? as date)
                                                OR CAST(ofm.fromTime as time) BETWEEN CAST(? as time) AND CAST (? as time) AND CAST(ofm.toTime as time) BETWEEN CAST(? as time) AND CAST (? as time))
                                    FOR JSON PATH) AS VARCHAR(MAX))""",(offer['offerId'],offer['fromDate'],offer['toDate'],offer['fromDate'],offer['toDate'],offer['fromTime'],offer['toTime'],offer['fromTime'],offer['toTime']))
            row = await db.fetchone()
            
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    dic['userId']=offer['userId']
                    dic['userName']=offer['userName']                   
                    data.append(dic)
        
        if len(data)!=0:
            return {
                "response":data,
                "statusCode":1
            }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as offerUserIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def offerDateDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        

        await db.execute(f"""SELECT CAST((SELECT ofm.*,(SELECT * FROM offerRules AS ofr WHERE ofr.offerId=ofm.offerId FOR JSON PATH)AS offerRulesDetails
                                            FROM  offerMaster as ofm
                                            WHERE ? BETWEEN ofm.fromDate and ofm.toDate
                                FOR JSON PATH) AS VARCHAR(MAX))""",(date))
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
        print("Exception as offerDateDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
async def offerDateBranchIdDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ofm.*,(SELECT * FROM offerRules AS ofr WHERE ofr.offerId=ofm.offerId FOR JSON PATH)AS offerRulesDetails
                                            FROM  offerMaster as ofm
                                            WHERE ? BETWEEN ofm.fromDate and ofm.toDate AND ofm.offerId NOT IN (SELECT offerId FROM offerMapping WHERE branchId =?)
                                FOR JSON PATH) AS VARCHAR(MAX))""",(date,branchId))
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
        print("Exception as offerDateBranchIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def offerDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ofm.*,case when CAST(GETDATE() as DATE)= ofm.toDate then 
					case when CAST(GETDATE() as TIME) between ofm.fromTime and ofm.totime THEN 'Not Expired' ELSE 'ExpiredByTime' END
					when CAST(GETDATE() as DATE)< ofm.toDate then 'Not Expired'  
					else 'ExpiredByDate' End as 'ExpireStatus',(SELECT * FROM offerRules AS ofr WHERE ofr.offerId=ofm.offerId FOR JSON PATH)AS offerRulesDetails
						FROM offerMaster AS ofm
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
        print("Exception as offerDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def offerParkingOwnerIdAmountDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT omv2.offerId, 
										omv2.offerHeading,
										omv2.offerDescription,
										omv2.offerCode,
										omv2.offerImageUrl,
										omv2.offerType,
										omv2.offerValue,
										omv2.termsAndConditions
								FROM offerMasterView2 AS omv2
								WHERE omv2.parkingOwnerId = ? 
									AND (? BETWEEN omv2.minAmt AND omv2.maxAmt) 
									AND omv2.offerTypePeriod = 'B' 
									AND omv2.offerMasterActiveStatus = 'A' 
									AND omv2.offerMappingActiveStatus = 'A'
									AND ((GETDATE() BETWEEN omv2.fromDate AND omv2.toDate) OR CONVERT(DATE, GETDATE()) = CONVERT(DATE, omv2.fromDate) OR CONVERT(DATE, GETDATE()) = CONVERT(DATE, omv2.fromDate))
									AND ( (CONVERT(TIME,GETDATE()) BETWEEN omv2.fromTime AND omv2.toTime) OR CONVERT(TIME, GETDATE()) = omv2.fromTime OR CONVERT(TIME, GETDATE()) = omv2.toTime)
                                FOR JSON PATH) AS VARCHAR(MAX))""",(parkingOwnerId,Amount))
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
        print("Exception as offerParkingOwnerIdAmountDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
async def offerBranchIdAmountDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ofm.*,(SELECT * FROM offerRules AS ofr WHERE ofr.offerId=ofm.offerId FOR JSON PATH)AS offerRulesDetails
						FROM offerMasterView2 as ofm
						WHERE (? BETWEEN minAmt AND maxAmt) AND branchId=? AND (GETDATE() BETWEEN ofm.fromDate AND ofm.toDate)
                                FOR JSON PATH) AS VARCHAR(MAX))""",(Amount,branchId))
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
        print("Exception as offerBranchIdAmountDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def offerBranchIdAmountTypePeriodDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ofm.*,(SELECT * FROM offerRules AS ofr WHERE ofr.offerId=ofm.offerId FOR JSON PATH)AS offerRulesDetails
						FROM offerMasterView2 as ofm
						WHERE (? BETWEEN minAmt AND maxAmt) AND branchId=? AND offerTypePeriod=? AND CAST(GETDATE()as DATE) BETWEEN ofm.fromDate AND ofm.toDate AND CAST(GETDATE() as TIME) between ofm.fromTime and ofm.totime
                                FOR JSON PATH) AS VARCHAR(MAX))""",(Amount,branchId,offerTypePeriod))
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
        print("Exception as offerBranchIdAmountTypePeriodDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def offerTypePeriodDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ofm.*
						FROM offerMaster AS ofm
						WHERE offerTypePeriod=? and CAST(getdate() AS DATE) between fromDate and toDate
                                FOR JSON PATH) AS VARCHAR(MAX))""",(offerTypePeriod))
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
        print("Exception as offerTypePeriodDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def offerTypePeriodActiveDetails(userId,Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId,offerTypePeriod,activeStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ofm.*
						FROM offerMaster AS ofm
						WHERE offerTypePeriod=? and activeStatus=? and CAST(getdate() AS DATE) between fromDate and toDate
                                FOR JSON PATH) AS VARCHAR(MAX))""",(offerTypePeriod,activeStatus))
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
        print("Exception as offerTypePeriodActiveDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

parkingPassDict = {
   "userId=True, Amount=True, fromDate=False, toDate=False, fromTime=False, toTime=False, branchId=True, parkingOwnerId=False, date=False, offerId=False, offerTypePeriod=False, activeStatus=False":offerUserBranchIdAmountDetails,
   "userId=True, Amount=True, fromDate=True, toDate=True, fromTime=False, toTime=False, branchId=True, parkingOwnerId=False, date=False, offerId=False, offerTypePeriod=False, activeStatus=False":offerUserBranchIdAmountDateDetails,
   "userId=False, Amount=False, fromDate=False, toDate=False, fromTime=False, toTime=False, branchId=False, parkingOwnerId=False, date=False, offerId=True, offerTypePeriod=False, activeStatus=False":offerIdDetails,
   "userId=True, Amount=True, fromDate=False, toDate=False, fromTime=True, toTime=True, branchId=True, parkingOwnerId=False, date=False, offerId=False, offerTypePeriod=False, activeStatus=False":offerUserBranchIdAmountTimeDetails,
   "userId=True, Amount=True, fromDate=True, toDate=True, fromTime=True, toTime=True, branchId=True, parkingOwnerId=False, date=False, offerId=False, offerTypePeriod=False, activeStatus=False":offerUserBranchIdAmountDateTimeDetails,
   "userId=True, Amount=False, fromDate=False, toDate=False, fromTime=False, toTime=False, branchId=False, parkingOwnerId=False, date=False, offerId=False, offerTypePeriod=False, activeStatus=False":offerUserIdDetails,
   "userId=False, Amount=False, fromDate=False, toDate=False, fromTime=False, toTime=False, branchId=False, parkingOwnerId=False, date=True, offerId=False, offerTypePeriod=False, activeStatus=False":offerDateDetails,
   "userId=False, Amount=False, fromDate=False, toDate=False, fromTime=False, toTime=False, branchId=True, parkingOwnerId=False, date=True, offerId=False, offerTypePeriod=False, activeStatus=False":offerDateBranchIdDetails,
   "userId=False, Amount=True, fromDate=False, toDate=False, fromTime=False, toTime=False, branchId=False, parkingOwnerId=True, date=False, offerId=False, offerTypePeriod=False, activeStatus=False":offerParkingOwnerIdAmountDetails,
   "userId=False, Amount=True, fromDate=False, toDate=False, fromTime=False, toTime=False, branchId=True, parkingOwnerId=False, date=False, offerId=False, offerTypePeriod=False, activeStatus=False":offerBranchIdAmountDetails,
   "userId=False, Amount=True, fromDate=False, toDate=False, fromTime=False, toTime=False, branchId=True, parkingOwnerId=False, date=False, offerId=False, offerTypePeriod=True, activeStatus=False":offerBranchIdAmountTypePeriodDetails,
   "userId=False, Amount=False, fromDate=False, toDate=False, fromTime=False, toTime=False, branchId=False, parkingOwnerId=False, date=False, offerId=False, offerTypePeriod=True, activeStatus=False":offerTypePeriodDetails,
   "userId=False, Amount=False, fromDate=False, toDate=False, fromTime=False, toTime=False, branchId=False, parkingOwnerId=False, date=False, offerId=False, offerTypePeriod=True, activeStatus=True":offerTypePeriodActiveDetails,
   "userId=False, Amount=False, fromDate=False, toDate=False, fromTime=False, toTime=False, branchId=False, parkingOwnerId=False, date=False, offerId=False, offerTypePeriod=False, activeStatus=False":offerDetails
}

@offerRouter.get('')
async def parkingOfferMaster(userId:Optional[int]=Query(None),Amount:Optional[str]=Query(None),fromDate:Optional[date]=Query(None),toDate:Optional[date]=Query(None),fromTime:Optional[time]=Query(None),toTime:Optional[time]=Query(None),branchId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None),date:Optional[date]=Query(None),offerId:Optional[int]=Query(None),offerTypePeriod:Optional[str]=Query(None),activeStatus:Optional[str]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"userId={True if userId else False}, Amount={True if Amount else False}, fromDate={True if fromDate else False}, toDate={True if toDate else False}, fromTime={True if fromTime else False}, toTime={True if toTime else False}, branchId={True if branchId else False}, parkingOwnerId={True if parkingOwnerId else False}, date={True if date else False}, offerId={True if offerId else False}, offerTypePeriod={True if offerTypePeriod else False}, activeStatus={True if activeStatus else False}"
        return await parkingPassDict[st](userId, Amount, fromDate, toDate, fromTime, toTime, branchId, parkingOwnerId, date, offerId, offerTypePeriod, activeStatus, db)
    
    except Exception as e:
        print("Exception as parkingOfferMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}
        
@offerRouter.post('')
async def postOfferMaster(request:schemas.OfferMaster,db:Cursor = Depends(get_cursor)):
    try:
        if request.offerRulesDetails!=None:
                r = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.offerRulesDetails)
                r = json.dumps(r,indent=4, sort_keys=True, default=str)
        else:
            r=None
        await db.execute(f"""EXEC [dbo].[postOfferMaster]
                                    @offerTypePeriod=?,
                                    @offerHeading=?,
                                    @offerDescription=?,
                                    @offerCode=?,
                                    @offerImageUrl=?,
                                    @fromDate=?,
                                    @toDate=?,
                                    @fromTime=?,
                                    @toTime=?,
                                    @offerType=?,
                                    @offerValue=?,
                                    @minAmt=?,
                                    @maxAmt=?,
                                    @noOfTimesPerUser=?,
                                    @activeStatus=?,
                                    @createdBy=?,
                                    @offerRulesDetailsJson=?""",
                                    
                                    (request.offerTypePeriod,
                                    request.offerHeading,
                                    request.offerDescription,
                                    request.offerCode,
                                    request.offerImageUrl,
                                    request.fromDate,
                                    request.toDate,
                                    request.fromTime,
                                    request.toTime,
                                    request.offerType,
                                    request.offerValue,
                                    request.minAmt,
                                    request.maxAmt,
                                    request.noOfTimesPerUser,
                                    request.activeStatus,
                                    request.createdBy,
                                    r))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            postOfferName.delay(int(row[2]),request.offerHeading,request.offerDescription)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postOfferMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}



@offerRouter.put('')
async def putOfferMaster(request:schemas.PutOfferMaster,db:Cursor = Depends(get_cursor)):
    try:
        if request.offerRulesDetails!=None:
                r = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.offerRulesDetails)
                r = json.dumps(r,indent=4, sort_keys=True, default=str)
        else:
            r=None
        await db.execute(f"""EXEC [dbo].[putOfferMaster]
                                    @offerId=?,
                                    @offerTypePeriod=?,
                                    @offerHeading=?,
                                    @offerDescription=?,
                                    @offerCode=?,
                                    @offerImageUrl=?,
                                    @fromDate=?,
                                    @toDate=?,
                                    @fromTime=?,
                                    @toTime=?,
                                    @offerType=?,
                                    @offerValue=?,
                                    @minAmt=?,
                                    @maxAmt=?,
                                    @noOfTimesPerUser=?,
                                    @activeStatus=?,
                                    @updatedBy=?,
                                    @offerRulesDetailsJson=?""",
                                    
                                    (request.offerId,
                                    request.offerTypePeriod,
                                    request.offerHeading,
                                    request.offerDescription,
                                    request.offerCode,
                                    request.offerImageUrl,
                                    request.fromDate,
                                    request.toDate,
                                    request.fromTime,
                                    request.toTime,
                                    request.offerType,
                                    request.offerValue,
                                    request.minAmt,
                                    request.maxAmt,
                                    request.noOfTimesPerUser,
                                    request.activeStatus,
                                    request.updatedBy,
                                    r
                                   ))
        row=await db.fetchone()
        
        await db.commit()
        if int(row[1])==1:
            postOfferName.delay(request.offerId,request.offerHeading,request.offerDescription)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}    

    except Exception as e:
        print("Exception as putOfferMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@offerRouter.delete('')
async def deleteOfferMaster(activeStatus:str,offerId:int,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE offerMaster SET activeStatus=? WHERE offerId=?",activeStatus,offerId)
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
        print("Exception as deleteOfferMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}