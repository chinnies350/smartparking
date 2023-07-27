from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from fastapi import Response
from aioodbc.cursor import Cursor
import routers
from routers.config import get_cursor
from typing import Optional
from fastapi import Query
# from datetime import time,date
import time
import json,os
import asyncio
from dotenv import load_dotenv
load_dotenv()

passBookingTransactionRouter = APIRouter(prefix="/passBookingTransaction",tags=['passBookingTransaction'])

async def getPassTransactionIdDetails(passTransactionId,dic):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?passTransactionId={passTransactionId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            dic['parkingName']=response['response'][0]['parkingName']
            response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/branchMaster?branchId={response['response'][0]['branchId']}")
            response = json.loads(response.text)
            dic['branchName']=response['response'][0]['branchName']
            dic['address1']=response['response'][0]['address1']
            dic['address2']=response['response'][0]['address2']
            dic['pincode']=response['response'][0]['pincode']
            dic['city']=response['response'][0]['city']
            dic['district']=response['response'][0]['district']
            dic['phoneNumber']=response['response'][0]['phoneNumber']

    except Exception as e:
        print("Exception as getPassTransactionIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def modifiedExtraFeatures(bookingPassId,dic):
    try:
        url = f"{os.getenv('BOOKING_URL')}/extraFeatures?bookingPassId={bookingPassId}"
        response = await routers.client.get(url)
        res= json.loads(response.text)
        if res['statusCode']==1:
            dic['extraFeaturesDetails']=res['response']
        else:
           dic['extraFeaturesDetails']=[]
    except Exception as e:
        print("Exception as modifiedExtraFeatures ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def modifiedFloorDetails(floorId,dic):
    try:
        response = await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/floorMaster?floorId={floorId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            dic['parkingOwnerId']=response['response'][0]['parkingOwnerId']
            dic['parkingName']=response['response'][0]['parkingName']
            dic['branchId']=response['response'][0]['branchId']
            dic['branchName']=response['response'][0]['branchName']
            response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/branchMaster?branchId={dic['branchId']}")
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                dic['branchPhoneNumber']=response['response'][0]['phoneNumber']
                dic['latitude']=response['response'][0]['latitude']
                dic['longitude']=response['response'][0]['longitude']
            else:
                dic['branchPhoneNumber']=""
                dic['latitude']=""
                dic['longitude']=""
        else:
            dic['parkingOwnerId']=""
            dic['parkingName']=""
            dic['branchId']=""
            dic['branchName']=""
            dic['branchPhoneNumber']=""
            dic['latitude']=""
            dic['longitude']=""

    except Exception as e:
        print("Exception as modifiedFloorDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def getExtraFeesFeaturesDetails(passBookingTransactionId,dic,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ef.*
                                                FROM extraFees as ef
                                                WHERE ef.bookingPassId = ? AND ef.bookingIdType = 'P'
                                                  FOR JSON PATH) AS  varchar(max))""",(passBookingTransactionId))
        
        row = await db.fetchone()
        extraFeesRes=[]
        if row[0] != None:
            for i in json.loads(row[0]):
                extraFeesRes.append({'extraFeesId':i['extraFeesId'],'bookingIdType':i['bookingIdType'],'bookingPassId':i['bookingPassId'],'priceId':i.get('priceId'),'count':i['count'],'extraFee':i['extraFee'],'extraFeesDetails':i.get('extraFeesDetails'),'createdDate':i['createdDate'],'createdBy':i['createdBy']})   
            dic['extraFeesDetail']=extraFeesRes
            response = await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/priceMaster?priceIds={extraFeesRes}")
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                dic['extraFeesTotalAmount']=response['response'][0]['extraFeesTotalAmount']
                dic['extraFeesAmount']=response['response'][0]['extraFeesAmount']
                dic['extraFeesTaxAmount']=response['response'][0]['extraFeesTaxAmount']
        await db.execute(f"""SELECT CAST((SELECT ef.*
                                                FROM extraFeatures as ef
                                                WHERE ef.bookingPassId = ? AND ef.bookingIdType = 'P'
                                                  FOR JSON PATH) AS  varchar(max))""",(passBookingTransactionId))
        
        row = await db.fetchone()
        extraFeaturesRes=[]
        if row[0] != None:
            for i in json.loads(row[0]):
                response = await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/floorfeatures?featuresId={i['floorFeaturesId']}")
                response = json.loads(response.text)
                extraFeaturesRes.append({'extraFeatureId':i['extraFeatureId'],'bookingIdType':i['bookingIdType'],'bookingPassId':i['bookingPassId'],'floorFeaturesId':i['floorFeaturesId'],'count':i['count'],'extraDetail':i.get('extraDetail'),'tax':response['response'][0]['tax'] if response['statusCode']==1 else "",'totalAmount':response['response'][0]['totalAmount'] if response['statusCode']==1 else "",'createdDate':i['createdDate'],'updatedDate':i.get('updatedDate')})

            dic['extraFeaturesDetail']=extraFeaturesRes
            response = await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/floorfeatures?featuresIds={extraFeaturesRes}")
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                dic['extraFeaturesTotalAmount']=response['response'][0]['extraFeaturesTotalAmount']
                dic['extraFeaturesAmount']=response['response'][0]['extraFeaturesAmount']
                dic['extraFeaturesTaxAmount']=response['response'][0]['extraFeaturesTaxAmount']
    except Exception as e:
        print("Exception as getExtraFeesFeaturesDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
        
async def getPassBookingTransactionIdDetails(slotId,passBookingTransactionId,passTransactionId,userId,type,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pbt.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=pbt.passBookingTransactionId FOR JSON PATH),'[]') AS vehicleDetails
                                                FROM passBookingTransaction AS pbt
                                                WHERE pbt.passBookingTransactionId = ?
                                                  FOR JSON PATH) AS  varchar(max))""",(passBookingTransactionId))
        row = await db.fetchone()
        
        data=[]
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                    getPassTransactionIdDetails(i['passTransactionId'],dic),
                                        getExtraFeesFeaturesDetails(i['passBookingTransactionId'],dic,db))
                data.append(dic)
            return {
                    "response": data,
                    "statusCode":1
                }
        return {
            "response": "Data Not Found",
            "statusCode": 0
        }

    except Exception as e:
        print("Exception as getPassBookingTransactionIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def getPassBookingTransactionDetails(slotId,passBookingTransactionId,passTransactionId,userId,type,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pbt.*
                                                FROM passBookingTransaction AS pbt
                                                  FOR JSON PATH) AS  varchar(max))""")
        row = await db.fetchone()
        
        
        if row[0] != None:
            return {
                    "response": json.loads(row[0]),
                    "statusCode":1
                }
        return {
            "response": "Data Not Found",
            "statusCode": 0
        }

    except Exception as e:
        print("Exception as getPassBookingTransactionDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
        
async def getPassBookingTransactionDetailsBasedOnpassBookingIdSlotId(slotId,passBookingTransactionId,passTransactionId,userId,type,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pbt.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=pbt.passBookingTransactionId and vh.slotId='{slotId}' FOR JSON PATH),'[]') AS vehicleDetails
                                                FROM passBookingTransaction AS pbt
                                                WHERE pbt.passBookingTransactionId = ?
                                                  FOR JSON PATH) AS  varchar(max))""",(passBookingTransactionId))
        row = await db.fetchone()
        
        data=[]
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                    getPassTransactionIdDetails(i['passTransactionId'],dic),
                    getExtraFeesFeaturesDetails(i['passBookingTransactionId'],dic,db))
                data.append(dic)
            return {
                    "response": data,
                    "statusCode":1
                }
        return {
            "response": "Data Not Found",
            "statusCode": 0
        }

    except Exception as e:
        print("Exception as getPassBookingTransactionDetailsBasedOnpassBookingIdSlotId ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def getParkingPassTransIdDetails(slotId,passBookingTransactionId,passTransactionId,userId,type,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT pbt.*,(SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=pbt.passBookingTransactionId FOR JSON PATH) AS vehicleDetails,
                                                        (SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=pbt.passBookingTransactionId FOR JSON PATH) AS extraFeaturesDetails,
                                                        (SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=pbt.passBookingTransactionId FOR JSON PATH) AS extraFeesDetails,
                                                        (SELECT us.* FROM userSlot AS us WHERE us.bookingPassId=pbt.passBookingTransactionId FOR JSON PATH) AS userSlotsDetails
                                        FROM passBookingTransaction AS pbt
                                        WHERE passTransactionId= ?
                                        FOR JSON PATH) AS  varchar(max))""",(passTransactionId))
        row = await db.fetchone()
        if row[0] != None:
            return {
                    "response": json.loads(row[0]),
                    "statusCode":1
                }
        return {
            "response": "Data Not Found",
            "statusCode": 0
        }

    except Exception as e:
        print("Exception as getParkingPassTransIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
        



async def getPassBookingTransactionDetailsBasedOnpassBookingIdType(passBookingTransactionId,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pbt.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=pbt.passBookingTransactionId FOR JSON PATH),'[]') AS vehicleDetails,
                                                'NULL' as extendAmount,
                                                'NULL' as extendTax,
                                                'NULL' as extendDayHour,
                                                'NULL' as remainingAmount,
                                                'NULL' as boookingAmount
                                                FROM passBookingTransaction AS pbt
                                                WHERE pbt.passBookingTransactionId = ?
                                                  FOR JSON PATH) AS  varchar(max))""",(passBookingTransactionId))
        row = await db.fetchone()
        data=[]
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                    getPassTransactionIdDetails(i['passTransactionId'],dic),
                    getExtraFeesFeaturesDetails(i['passBookingTransactionId'],dic,db))
                data.append(dic)
            if data!=None and data !=[]:
             
                return {
                        "response": data,
                        "statusCode":1
                    }
            else:
                return {
                    "response": "Data Not Found",
                    "statusCode": 0
                    }
        return {
            "response": "Data Not Found",
            "statusCode": 0
        }

    except Exception as e:
        print("Exception as getPassBookingTransactionDetailsBasedOnpassBookingIdSlotId ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }


async def getParkingBookingUserIdDetails(slotId,passBookingTransactionId,passTransactionId,userId,type,db):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?userId={userId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            if type=='H':
                await db.execute(f"""SELECT CAST((SELECT pbtm.*,
                                                        ISNULL((SELECT vh.* 
                                                                FROM vehicleHeader AS vh 
                                                                WHERE vh.bookingPassId=pbtm.passBookingTransactionId AND vh.bookingIdType = 'P' 
                                                                FOR JSON PATH),'[]') AS vehicleDetails,
                                                        
                                                        ISNULL((SELECT exf.* 
                                                                FROM extraFees AS exf 
                                                                WHERE exf.bookingPassId=pbtm.passBookingTransactionId AND exf.bookingIdType='P' 
                                                                FOR JSON PATH),'[]')AS extraFeesDetails,
                                                        ISNULL((SELECT uss.*
                                                                FROM userSLot AS uss 
                                                                WHERE uss.bookingPassId=pbtm.passBookingTransactionId and uss.bookingIdType='P' 
                                                                FOR JSON PATH),'[]')AS userSlotDetails
                                            FROM passBookingTransaction AS pbtm
                                            WHERE pbtm.passBookingTransactionId IN (
                                                    SELECT pbt.passBookingTransactionId 
                                                    FROM passBookingTransaction AS pbt
                                                    INNER JOIN vehicleHeader AS vh 
                                                    ON vh.bookingPassId = pbt.passBookingTransactionId
                                                    WHERE pbt.passTransactionId IN {(tuple(i['parkingPassTransId'] for i in response['response'])+tuple('0'))} AND vh.bookingIdType = 'P' 
                                                    AND vh.vehicleStatus='O')
                                            FOR JSON PATH, INCLUDE_NULL_VALUES) AS  varchar(max))""")

                row = await db.fetchone()
            elif type=='R':
                await db.execute(f"""SELECT CAST((SELECT pbtm.*,
                                                        ISNULL((SELECT vh.* 
                                                                FROM vehicleHeader AS vh 
                                                                WHERE vh.bookingPassId=pbtm.passBookingTransactionId AND vh.bookingIdType = 'P' 
                                                                FOR JSON PATH),'[]') AS vehicleDetails,
                                                        
                                                        ISNULL((SELECT exf.* 
                                                                FROM extraFees AS exf 
                                                                WHERE exf.bookingPassId=pbtm.passBookingTransactionId AND exf.bookingIdType='P' 
                                                                FOR JSON PATH),'[]')AS extraFeesDetails,
                                                        ISNULL((SELECT uss.*
                                                                FROM userSLot AS uss 
                                                                WHERE uss.bookingPassId=pbtm.passBookingTransactionId and uss.bookingIdType='P' 
                                                                FOR JSON PATH),'[]')AS userSlotDetails
                                            FROM passBookingTransaction AS pbtm
                                            WHERE pbtm.passBookingTransactionId IN (
                                                    SELECT pbt.passBookingTransactionId 
                                                    FROM passBookingTransaction AS pbt
                                                    INNER JOIN vehicleHeader AS vh 
                                                    ON vh.bookingPassId = pbt.passBookingTransactionId
                                                    WHERE pbt.passTransactionId IN {(tuple(i['parkingPassTransId'] for i in response['response'])+tuple('0'))} AND vh.bookingIdType = 'P' 
                                                    AND vh.vehicleStatus!='O' or vh.vehicleStatus IS NULL)
                                            FOR JSON PATH, INCLUDE_NULL_VALUES) AS  varchar(max))""")

                row = await db.fetchone()
            
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await asyncio.gather(modifiedExtraFeatures(i['passBookingTransactionId'],dic),
                                            modifiedFloorDetails(i['floorId'],dic))        
                return {
                        "response": dic,
                        "statusCode":1
                    }
            return {
                "response": "Data Not Found",
                "statusCode": 0
            }

    except Exception as e:
        print("Exception as getParkingBookingUserIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }


passBookingDict = {
    "slotId=True, passBookingTransactionId=True, passTransactionId=False, userId=False, type=False":getPassBookingTransactionDetailsBasedOnpassBookingIdSlotId,
    "slotId=False, passBookingTransactionId=True, passTransactionId=False, userId=False, type=False":getPassBookingTransactionIdDetails,
    "slotId=False, passBookingTransactionId=False, passTransactionId=True, userId=False, type=False":getParkingPassTransIdDetails,
    "slotId=False, passBookingTransactionId=False, passTransactionId=False, userId=True, type=True":getParkingBookingUserIdDetails,
    "slotId=False, passBookingTransactionId=False, passTransactionId=False, userId=False, type=False":getPassBookingTransactionDetails
    
}

@passBookingTransactionRouter.get('')
async def getPassBookingTransaction(slotId:Optional[int]=Query(None),passBookingTransactionId:Optional[int]=Query(None), passTransactionId:Optional[int]=Query(None), userId:Optional[int]=Query(None), type:Optional[str]=Query(None) ,db: Cursor = Depends(get_cursor)):
    try:
        st = f"slotId={True if slotId else False}, passBookingTransactionId={True if passBookingTransactionId else False}, passTransactionId={True if passTransactionId else False}, userId={True if userId else False}, type={True if type else False}"
        return await passBookingDict[st](slotId, passBookingTransactionId, passTransactionId, userId, type, db)
        
            
    except Exception as e:
        print("Exception as getpassBookingTransaction ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }