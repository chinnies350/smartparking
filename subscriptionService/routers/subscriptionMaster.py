import json
from sqlite3 import Cursor
import routers
from fastapi.routing import APIRouter
from routers.config import get_cursor
from fastapi import Depends
from typing import Optional
from fastapi import Query
import schemas
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

subscriptionRouter = APIRouter(prefix='/subscriptionMaster')



async def getTaxDetailsBasedOnTaxId(taxId):
    try:
        response = await routers.client.get(f"{os.getenv('ADMIN_SERVICE_URL')}/taxMaster?taxId={taxId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0]
        return None
    except Exception as e:
        print("Exception as getTaxDetailsBasedOnTaxId ",str(e))
        return None


async def getDetailsBasedOnSubscriptionId(subscriptionId,db):
    try:
       
        await db.execute(f"""SELECT CAST((SELECT sm.* 
                                                FROM subscriptionMaster AS sm
                                                WHERE subscriptionId = ? FOR JSON PATH) AS  varchar(max))""", (subscriptionId))
        row = await db.fetchone()
        if row[0] != None:
            return {
                "statusCode":1,
                "response":json.loads(row[0])
                
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
async def getDetailsBasedOnTaxId(taxId,db):
    try:
        await db.execute(f"""SELECT CAST(MAX(sm.createdDate) as date)AS subscriptionMaster
                                FROM subscriptionMaster AS sm
                                WHERE sm.taxId = ?
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

async def getDetailsBasedOnActiveStatus(activeStatus, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT sm.* 
                                                FROM subscriptionMaster AS sm
                                                WHERE activeStatus = ? AND (GETDATE() BETWEEN validityFrom AND validityTo) FOR JSON PATH) AS  varchar(max))""", (activeStatus))
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
        print("Exception as getDetailsBasedOnActiveStatus ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
async def getSubscriptionDetails(db):
    try:
        
        await db.execute(f"SELECT CAST((SELECT sm.* FROM subscriptionMaster AS sm  FOR JSON PATH) AS  varchar(max))")
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
        print("Exception as getSubscriptionDetails ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@subscriptionRouter.get('')
async def getSubscriptionMaster(subscriptionId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),taxId:Optional[int]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        if subscriptionId:
            return await getDetailsBasedOnSubscriptionId(subscriptionId, db)
        elif activeStatus:
            return await getDetailsBasedOnActiveStatus(activeStatus, db)
        elif taxId:
            return await getDetailsBasedOnTaxId(taxId, db)
        else:
            return await getSubscriptionDetails(db)
    except Exception as e:
        print("Exception as getSubscriptionMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@subscriptionRouter.post('')
async def postSubscriptionMaster(request:schemas.SubscriptionMaster,db:Cursor = Depends(get_cursor)):
    try:

        taxPercentage=await getTaxDetailsBasedOnTaxId(request.taxId)
        if taxPercentage:
            tax=((request.totalAmount * taxPercentage.get('taxPercentage')) / 100)
            taxName=taxPercentage.get('taxName')
        else:
            tax=0
            taxName=None
        await db.execute(f"""EXEC [dbo].[postSubscriptionMaster]
                                    @subscriptionName=?,
                                    @validity=?,
                                    @offerType=?,
                                    @offerValue=?,
                                    @parkingLimit=?,
                                    @rules=?,
                                    @taxId=?,
                                    @taxName=?,
                                    @tax=?,
                                    @totalAmount=?,
                                    @validityFrom=?,
                                    @validityTo=?,
                                    @activeStatus=?,
                                    @createdBy=?""",
                                (
                                request.subscriptionName,
                                request.validity,
                                request.offerType,
                                request.offerValue,
                                request.parkingLimit,
                                request.rules,
                                request.taxId,
                                taxName,
                                tax,
                                request.totalAmount,
                                request.validityFrom,
                                request.validityTo,
                                request.activeStatus,
                                request.createdBy,
                                ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postsubscriptionMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@subscriptionRouter.put('')
async def putSubscriptionMaster(request:schemas.PutSubscriptionMaster,db:Cursor = Depends(get_cursor)):
    try:
        taxPercentage=await getTaxDetailsBasedOnTaxId(request.taxId)
        if taxPercentage:
            tax=((request.totalAmount * taxPercentage.get('taxPercentage')) / 100)
            taxName=taxPercentage.get('taxName')
        else:
            tax=0
            taxName=None
        await db.execute(f"""EXEC [dbo].[putSubscriptionMaster]
                                    @subscriptionName=?,
                                    @validity=?,
                                    @offerType=?,
                                    @offerValue=?,
                                    @parkingLimit=?,
                                    @rules=?,
                                    @tax=?,
                                    @totalAmount=?,
                                    @validityFrom=?,
                                    @validityTo=?,
                                    @updatedBy=?,
                                    @activeStatus=?,
                                    @subscriptionId=?,
                                    @taxId=?,
                                    @taxName=?""",
                                (
                                request.subscriptionName,
                                request.validity,
                                request.offerType,
                                request.offerValue,
                                request.parkingLimit,
                                request.rules,
                                tax,
                                request.totalAmount,
                                request.validityFrom,
                                request.validityTo,
                                request.updatedBy,
                                request.activeStatus,
                                request.subscriptionId,
                                request.taxId,
                                taxName))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putSubscriptionMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}



@subscriptionRouter.delete('')
async def deleteSubscriptionMaster(subscriptionId:int,activeStatus:str,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE subscriptionMaster SET activeStatus=? WHERE subscriptionId=?",activeStatus,subscriptionId)
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
        print("Exception as deleteSubscriptionMaster ",str(e))
        return{"stausCode":0, "response":"Server Error"}