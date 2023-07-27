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

offerRulesRouter = APIRouter(prefix='/offerRules')


def callFunction(i):
    i=i.dict()
    ruleTypeName=redis_client.hget('configMaster', i['ruleType'])
    i['ruleTypeName']=ruleTypeName.decode("utf-8") if ruleTypeName else None
    return i

async def offerRuleIdDetails(offerRuleId,offerId, activeStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ofr.*, om.offerHeading
                                            FROM offerRules as ofr
                                            INNER JOIN offerMaster as om 
                                            ON om.offerId = ofr.offerId
                                            WHERE ofr.offerRuleId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(offerRuleId))
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
        print("Exception as offerRuleIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
async def offerIdDetails(offerRuleId,offerId, activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ofr.*, om.offerHeading
                                            FROM offerRules as ofr
                                            INNER JOIN offerMaster as om 
                                            ON om.offerId = ofr.offerId
                                            WHERE ofr.offerId=?
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

async def activeStatusDetails(offerRuleId,offerId, activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ofr.*, om.offerHeading
                                            FROM offerRules as ofr
                                            INNER JOIN offerMaster as om 
                                            ON om.offerId = ofr.offerId
                                            WHERE ofr.activeStatus=?
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

async def offerRulesDetails(offerRuleId,offerId, activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ofr.*, om.offerHeading
                                            FROM offerRules as ofr
                                            INNER JOIN offerMaster as om 
                                            ON om.offerId = ofr.offerId
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
        print("Exception as offerRulesDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

parkingPassDict = {
   "offerRuleId=True, offerId=False, activeStatus=False":offerRuleIdDetails,
   "offerRuleId=False, offerId=True, activeStatus=False":offerIdDetails,
   "offerRuleId=False, offerId=False, activeStatus=True":activeStatusDetails,
   "offerRuleId=False, offerId=False, activeStatus=False":offerRulesDetails
   
}

@offerRulesRouter.get('')
async def getOfferRules(offerRuleId:Optional[int]=Query(None),offerId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"offerRuleId={True if offerRuleId else False}, offerId={True if offerId else False}, activeStatus={True if activeStatus else False}"
        return await parkingPassDict[st](offerRuleId, offerId, activeStatus,db)
    except Exception as e:
        print("Exception as getOfferRules ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@offerRulesRouter.post('')
async def postOfferRules(request:schemas.PostOfferRulesDetails,db:Cursor = Depends(get_cursor)):
    try:
        if request.offerRulesDetails!=None:
                r = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.offerRulesDetails)
                offerRulesDetailsJson=json.dumps(r,indent=4, sort_keys=True, default=str)
        else:
            offerRulesDetailsJson=None
        print(offerRulesDetailsJson)
        await db.execute(f"""EXEC [dbo].[postOfferRules]
                                     @offerId=?,
                                     @offerRulesDetailsJson=?""",
                                    (request.offerId,
                                    offerRulesDetailsJson))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postOfferRules ",str(e))
        return{"statusCode":0,"response":"Server Error"}



@offerRulesRouter.put('')
async def putOfferRules(request:schemas.PutOfferRulesDetails,db:Cursor = Depends(get_cursor)):
    try:
        r = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.offerRulesDetails)
        await db.execute(f"""EXEC [dbo].[putOfferRules]
                                    @offerRulesDetailsJson=?""",
                                    json.dumps(r,indent=4, sort_keys=True, default=str
                                   ))
        row=await db.fetchone()
        
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}    

    except Exception as e:
        print("Exception as putOfferRules ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@offerRulesRouter.delete('')
async def deleteofferRules(activeStatus:str,offerRuleId:int,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE offerRules SET activeStatus=? WHERE offerRuleId=?",activeStatus,offerRuleId)
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
        print("Exception as deleteOfferRules ",str(e))
        return{"statusCode":0,"response":"Server Error"}