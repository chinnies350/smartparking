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
from joblib import Parallel, delayed

load_dotenv()

offerMappingRouter = APIRouter(prefix='/offerMapping')


def callFunction(i):
    return i.dict()

async def offerMappingIdDetails(offerMappingId,parkingOwnerId,branchId,offerId, activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ofm.offerMappingId,ofm.parkingOwnerId,ofm.branchId,ofm.parkingName,ofm.branchName,ofm.offerId,ofm.activeStatus,
                                                    om.offerHeading,om.fromDate,om.toDate,om.fromTime,om.toTime,
                                                    om.maxAmt,om.minAmt,om.noOfTimesPerUser,om.offerCode,om.offerDescription,om.offerImageUrl,om.offerType,om.offerValue,om.offerTypePeriod,
                                                    (SELECT ors.offerRule,ors.offerRuleId,ors.ruleType FROM offerRules as ors WHERE om.offerId=ors.offerId and ors.activeStatus='A' for json path) as offerRulesDetails 
                                                    FROM offerMapping as ofm
                                                    INNER JOIN offerMaster AS om 
                                                    ON om.offerId=ofm.offerId
                                                    WHERE offerMappingId=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(offerMappingId))
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
        print("Exception as offerMappingIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def parkingOwnerIdDetails(offerMappingId,parkingOwnerId,branchId,offerId, activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ofm.offerMappingId,ofm.parkingOwnerId,ofm.branchId,ofm.parkingName,ofm.branchName,ofm.offerId,ofm.activeStatus,
                                                    om.offerHeading,om.fromDate,om.toDate,om.fromTime,om.toTime,
                                                    om.maxAmt,om.minAmt,om.noOfTimesPerUser,om.offerCode,om.offerDescription,om.offerImageUrl,om.offerType,om.offerValue,om.offerTypePeriod,
                                                    (SELECT ors.offerRule,ors.offerRuleId,ors.ruleType FROM offerRules as ors WHERE om.offerId=ors.offerId and ors.activeStatus='A' for json path) as offerRulesDetails 
                                                    FROM offerMapping as ofm
                                                    INNER JOIN offerMaster AS om 
                                                    ON om.offerId=ofm.offerId
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
        print("Exception as parkingOwnerIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchIdDetails(offerMappingId,parkingOwnerId,branchId,offerId, activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ofm.offerMappingId,ofm.parkingOwnerId,ofm.branchId,ofm.parkingName,ofm.branchName,ofm.offerId,ofm.activeStatus,
                                                    om.offerHeading,om.fromDate,om.toDate,om.fromTime,om.toTime,
                                                    om.maxAmt,om.minAmt,om.noOfTimesPerUser,om.offerCode,om.offerDescription,om.offerImageUrl,om.offerType,om.offerValue,om.offerTypePeriod,
                                                    (SELECT ors.offerRule,ors.offerRuleId,ors.ruleType FROM offerRules as ors WHERE om.offerId=ors.offerId and ors.activeStatus='A' for json path) as offerRulesDetails 
                                                    FROM offerMapping as ofm
                                                    INNER JOIN offerMaster AS om 
                                                    ON om.offerId=ofm.offerId
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
        print("Exception as branchIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def offerIdDetails(offerMappingId,parkingOwnerId,branchId,offerId, activeStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ofm.offerMappingId,ofm.parkingOwnerId,ofm.branchId,ofm.parkingName,ofm.branchName,ofm.offerId,ofm.activeStatus,
                                                    om.offerHeading,om.fromDate,om.toDate,om.fromTime,om.toTime,
                                                    om.maxAmt,om.minAmt,om.noOfTimesPerUser,om.offerCode,om.offerDescription,om.offerImageUrl,om.offerType,om.offerValue,om.offerTypePeriod,
                                                    (SELECT ors.offerRule,ors.offerRuleId,ors.ruleType FROM offerRules as ors WHERE om.offerId=ors.offerId and ors.activeStatus='A' for json path) as offerRulesDetails 
                                                    FROM offerMapping as ofm
                                                    INNER JOIN offerMaster AS om 
                                                    ON om.offerId=ofm.offerId
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

async def activeStatusDetails(offerMappingId,parkingOwnerId,branchId,offerId, activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ofm.offerMappingId,ofm.parkingOwnerId,ofm.branchId,ofm.parkingName,ofm.branchName,ofm.offerId,ofm.activeStatus,
                                                    om.offerHeading,om.fromDate,om.toDate,om.fromTime,om.toTime,
                                                    om.maxAmt,om.minAmt,om.noOfTimesPerUser,om.offerCode,om.offerDescription,om.offerImageUrl,om.offerType,om.offerValue,om.offerTypePeriod,
                                                    (SELECT ors.offerRule,ors.offerRuleId,ors.ruleType FROM offerRules as ors WHERE om.offerId=ors.offerId and ors.activeStatus='A' for json path) as offerRulesDetails 
                                                    FROM offerMapping as ofm
                                                    INNER JOIN offerMaster AS om 
                                                    ON om.offerId=ofm.offerId
                                                    WHERE ofm.activeStatus=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus))
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
        print("Exception as activeStatusDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def offerMappingDetails(offerMappingId,parkingOwnerId,branchId,offerId, activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ofm.offerMappingId,ofm.parkingOwnerId,ofm.branchId,ofm.parkingName,ofm.branchName,ofm.offerId,ofm.activeStatus,
                                                    om.offerHeading,om.fromDate,om.toDate,om.fromTime,om.toTime,
                                                    om.maxAmt,om.minAmt,om.noOfTimesPerUser,om.offerCode,om.offerDescription,om.offerImageUrl,om.offerType,om.offerValue,om.offerTypePeriod,
                                                    (SELECT ors.offerRule,ors.offerRuleId,ors.ruleType FROM offerRules as ors WHERE om.offerId=ors.offerId and ors.activeStatus='A' for json path) as offerRulesDetails 
                                                    FROM offerMapping as ofm
                                                    INNER JOIN offerMaster AS om 
                                                    ON om.offerId=ofm.offerId
                                                    
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
        print("Exception as offerMappingDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


parkingPassDict = {
   "offerMappingId=True, parkingOwnerId=False, branchId=False, offerId=False, activeStatus=False":offerMappingIdDetails,
   "offerMappingId=False, parkingOwnerId=True, branchId=False, offerId=False, activeStatus=False":parkingOwnerIdDetails,
   "offerMappingId=False, parkingOwnerId=False, branchId=True, offerId=False, activeStatus=False":branchIdDetails,
   "offerMappingId=False, parkingOwnerId=False, branchId=False, offerId=True, activeStatus=False":offerIdDetails,
   "offerMappingId=False, parkingOwnerId=False, branchId=False, offerId=False, activeStatus=True":activeStatusDetails,
   "offerMappingId=False, parkingOwnerId=False, branchId=False, offerId=False, activeStatus=False":offerMappingDetails
   
}

@offerMappingRouter.get('')
async def getofferMapping(offerMappingId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),offerId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"offerMappingId={True if offerMappingId else False}, parkingOwnerId={True if parkingOwnerId else False}, branchId={True if branchId else False}, offerId={True if offerId else False}, activeStatus={True if activeStatus else False}"
        return await parkingPassDict[st](offerMappingId, parkingOwnerId, branchId, offerId, activeStatus,db)
    except Exception as e:
        print("Exception as getofferMapping ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@offerMappingRouter.post('')
async def postOfferMapping(request:schemas.OfferMapping,db:Cursor = Depends(get_cursor)):
    try:
        parkingName = redis_client.hget('parkingOwnerMaster', request.parkingOwnerId)
        branchName = redis_client.hget('branchMaster', request.branchId)
        parkingName=parkingName.decode("utf-8") if parkingName else None
        branchName=branchName.decode("utf-8") if branchName else None
        
        await db.execute(f"""EXEC [dbo].[postOfferMapping]
                                    @parkingOwnerId=?,
                                    @parkingName=?,
                                    @branchId=?,
                                    @branchName=?,
                                    @offerId=?,
                                    @activeStatus=?,
                                    @createdBy=?""",
                                    (request.parkingOwnerId,
                                    parkingName,
                                    request.branchId,
                                    branchName,
                                    request.offerId,
                                    request.activeStatus,
                                    request.createdBy))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postOfferMapping ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@offerMappingRouter.delete('')
async def deleteOfferMapping(activeStatus:str,offerMappingId:int,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE offerMapping SET activeStatus=? WHERE offerMappingId=?",activeStatus,offerMappingId)
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
        print("Exception as deleteOfferMapping ",str(e))
        return{"statusCode":0,"response":"Server Error"}