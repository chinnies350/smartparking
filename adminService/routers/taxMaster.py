import json
from sqlite3 import Cursor
from fastapi.routing import APIRouter
from routers.config import get_cursor
from fastapi import Depends
from typing import Optional
from fastapi import Query
import schemas
import asyncio
import routers
import os
from task import postTaxName

taxRouter = APIRouter(prefix='/taxMaster')

async def getFloorFeaturesTaxId(taxId):
    try:
        response = await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/floorfeatures?taxId={taxId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getFloorFeaturesTaxId ",str(e))
        return ""

async def getPriceTaxId(taxId):
    try:
        response = await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/priceMaster?taxId={taxId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getPriceTaxId ",str(e))
        return ""

async def getParkingPassConfigTaxId(taxId):
    try:
        # type-T means taxMaxDate calculation
        response = await routers.client.get(f"{os.getenv('PARKING_PASS_MODULE_URL')}/parkingPassConfig?taxId={taxId}&type='T'")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getParkingPassConfigTaxId ",str(e))
        return ""

async def getPassTransactionTaxId(taxId):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?taxId={taxId}&type='T'")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getPassTransactionTaxId ",str(e))
        return ""


async def getSubscriptionTaxId(taxId):
    try:
        response = await routers.client.get(f"{os.getenv('SUBSCRIPTION_URL')}/subscriptionMaster?taxId={taxId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getSubscriptionTaxId ",str(e))
        return ""


async def getUserSubscriptionTaxId(taxId):
    try:
        response = await routers.client.get(f"{os.getenv('SUBSCRIPTION_URL')}/userSubscriptionMaster?taxId={taxId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getUserSubscriptionTaxId ",str(e))
        return ""


async def modifiedDataFloorFeatures(taxId):
    taxDetails = await getFloorFeaturesTaxId(taxId)
    return taxDetails

async def modifiedDataPrice(taxId):
    taxDetails = await getPriceTaxId(taxId)
    return taxDetails

async def modifiedDataParkingPassConfig(taxId):
    taxDetails = await getParkingPassConfigTaxId(taxId)
    return taxDetails

async def modifiedDataPassTransaction(taxId):
    taxDetails = await getPassTransactionTaxId(taxId)
    return taxDetails

async def modifiedDataSubscriptionMaster(taxId):
    taxDetails = await getSubscriptionTaxId(taxId)
    return taxDetails

async def modifiedDataUserSubscription(taxId):
    taxDetails = await getUserSubscriptionTaxId(taxId)
    return taxDetails

@taxRouter.get('')
async def getTaxMaster(taxId:Optional[int]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[getTaxMaster] ?""",taxId)
        rows=await db.fetchone()
        await db.commit()
        if rows[0]:
            return {"statusCode": 1,"response":json.loads(rows[0]) if rows[0] != None else []}
        else:
            return {
                    "statusCode":0,
                    "response":"Data Not Found"
                    }
    except Exception as e:
        print("Exception as getTaxMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@taxRouter.post('')
async def postTaxMaster(request:schemas.TaxMaster,db:Cursor = Depends(get_cursor)):
    try:
        
        await db.execute(f"""EXEC [dbo].[postTaxMaster] 
                                @serviceName=?,
                                @taxName=?,
                                @taxDescription=?,
                                @taxPercentage=?,
                                @activeStatus=?,
                                @effectiveFrom=?,
                                @effectiveTill=?,
                                @createdBy=?""",
                                (request.serviceName,
                                request.taxName,
                                request.taxDescription,
                                request.taxPercentage,
                                request.activeStatus,
                                request.effectiveFrom,
                                request.effectiveTill,
                                request.createdBy))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            postTaxName.delay(int(row[2]),request.taxName)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postTaxMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@taxRouter.put('')
async def putTaxMaster(request:schemas.PutTaxMaster,db:Cursor = Depends(get_cursor)):
    try:
        maxDates=await asyncio.gather(
                                        modifiedDataFloorFeatures(request.taxId),
                                        modifiedDataPrice(request.taxId),
                                        modifiedDataParkingPassConfig(request.taxId),
                                        modifiedDataPassTransaction(request.taxId),
                                        modifiedDataSubscriptionMaster(request.taxId),
                                        modifiedDataUserSubscription(request.taxId)
                                        )
        
        if max(maxDates):
            maxDates=max(maxDates)
        else:
            maxDates=None
        
        await db.execute(f"""EXEC [dbo].[putTaxMaster] 
                               @taxId=?,
                               @taxName=?,
                               @serviceName=?,
                               @taxDescription=?,
                               @taxPercentage=?,
                               @activeStatus=?,
                               @effectiveFrom=?,
                               @updatedBy=?,
                               @MaxDate=?
                               """,
                               (
                               request.taxId,
                               request.taxName,
                               request.serviceName,
                               request.taxDescription,
                               request.taxPercentage,
                               request.activeStatus,
                               request.effectiveFrom,
                               request.updatedBy,
                               maxDates))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            postTaxName.delay(int(row[2]),request.taxName)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}
        
        
    except Exception as e:
        print("Exception as putTaxMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@taxRouter.delete('')
async def deleteTaxMaster(taxId:int,activeStatus:str,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE TaxMaster SET activeStatus=? WHERE taxId=?",activeStatus,taxId)
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
                    "response": "Data Not Deleted"}

    except Exception as e:
        print("Exception as deleteTaxMaster ",str(e))
        return{"stausCode":0, "response":"Server Error"}