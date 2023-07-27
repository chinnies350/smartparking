# try:
from fastapi.routing import APIRouter
from fastapi import BackgroundTasks, Depends
from aioodbc.cursor import Cursor
from eventsServer import publish
import schemas
# from routers.config import engine 
from routers.config import get_cursor
from task import passlot

from datetime import datetime
from routers.config import get_cursor,redis_client
import json
from typing import Optional
from fastapi import Query
from joblib import Parallel, delayed 
from dotenv import load_dotenv
load_dotenv()
import asyncio
import routers
import os,json
from datetime import datetime,time,date
#from task import bookingmail,bookingdatetimeExtendmail,putbookingpaidAmountdmail,putPaymentStatusmail
# except Exception as e:
#     print(f"module not found {str(e)}")



router = APIRouter(prefix="/booking",tags=['booking'])

routerDateTimeExtend = APIRouter(
    prefix="/bookingMasterDateTimeExtend", tags=['booking'])

routerpaidAmount = APIRouter(prefix="/bookingMasterPaidAmount",tags=['booking'])

def callFunction(i):
    return i.dict()

def VehicleMasterCallFunction(i):
    i=i.dict()
    vehicleDetails=redis_client.hget('vehicleConfigMaster', i['vehicleType'])
    i['vehicleTypeName'],i['vehicleImageUrl']=tuple(json.loads(vehicleDetails.decode("utf-8")).values()) if vehicleDetails else None
    return i


async def getConfigMasterNameByConfigId(configId):
    try:
        response =  await routers.client.get(f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configId={configId}")
        response = json.loads(response.text)
        if response['statusCode'] ==1 :
            return response['response'][0]['configName']
        return ''
    except Exception as e:
        print("Exception as getConfigMasterNameByConfigId ",str(e))
        return "" 

async def getvehicleconfigmaster(vehicleType):
    try:
        response =  await routers.client.get(f"{os.getenv('ADMIN_SERVICE_URL')}/vehicleConfigMaster?vehicleConfigId={vehicleType}")
        response = json.loads(response.text)
        if response['statusCode'] ==1 :
            for i in response['response']:              
                return {
                        'vehicleTypeName':i['vehicleName'],
                        'vehicleImageUrl':i['vehicleImageUrl']
                }

        return {}

    except Exception as e:
        print("Exception as getvehicleconfigmaster",str(e))
        return {}

async def getfloorfeaturesOnextraFeatureId(floorFeaturesId):
    try:
        url = f"{os.getenv('SLOT_SERVICE_URL')}/floorfeatures?featuresId={floorFeaturesId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:              
                return {
                        'featureName':i['featureName'],
                        'tax':i['tax'],
                        'totalAmount':i['totalAmount']
                }
        return {}

    except Exception as e:
        print("Exception as getfloorfeaturesOnextraFeatureId",str(e))
        return {}

async def getbranchDetails(branchId):
    try:
        url = f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/branchMaster?branchId={branchId}"       
        response = await routers.client.get(url)       
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:              
                return [{
                        'address1':i['address1'],
                        'address2':i['address2'],
                        'district':i['district'],
                        'state':i['state'],
                        'city':i['city'],
                        'pincode':i['pincode'],
                        'latitude':i['latitude'],
                        'longitude':i['longitude']
                }]

        return []

    except Exception as e:
        print("Exception as getbranchDetails ",str(e))
        return {}

async def getbookingbranchDetails(branchId):
    try:
        url = f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/branchMaster?branchId={branchId}"       
        response = await routers.client.get(url)       
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:              
                return {
                        'address1':i['address1'],
                        'address2':i['address2'],
                        'district':i['district'],
                        'state':i['state'],
                        'city':i['city'],
                        'pincode':i['pincode'],
                        'branchPhoneNumber':i['phoneNumber'],
                        'latitude':i['latitude'],
                        'longitude':i['longitude']
                }

        return []

    except Exception as e:
        print("Exception as getbookingbranchDetails ",str(e))
        return {}

async def getslotdetailsbasedonslot(slotId):
    try:
        url=f"{os.getenv('SLOT_SERVICE_URL')}/parkingSlot?parkingSlotId={slotId}"
        print('url',url)
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:
                return {
                            'parkingLotLineId':i['parkingLotLineId'],
                            'slotNumber':i['slotNumber'],
                            'rowId':i['rowId'],
                            'columnId':i['columnId'],
                            'laneNumber':i['laneNumber'],
                            'slotactiveStatus':i['activeStatus'],
                            'slotState':i['slotState']

                        }
        return ""
    except Exception as e:
        print(f'error in getslotdetailsbasedonslot{str(e)}')
        return {}

async def getbookingAmount(floorFeaturesId,bookingPassId):
    try:
        url = f"{os.getenv('BOOKING_URL')}/extraFeatures?floorFeaturesId={floorFeaturesId}&bookingPassId={bookingPassId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:             
                return {
                        'boookingAmount':i['boookingAmount']
                }

        return ""

    except Exception as e:
        print(f'error in getbookingAmount {str(e)}')
        return {}

async def getbookingAmountandTaxAmount(floorFeaturesId,bookingPassId):
    try:
        url = f"{os.getenv('BOOKING_URL')}/extraFeatures?floorFeaturesId={floorFeaturesId}&bookingPassId={bookingPassId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:             
                return {
                        'boookingAmount':i['boookingAmount'],
                        'bookingTax':i['bookingTax']
                }

        return {}

    except Exception as e:
        print(f'error in getbookingAmountandTaxAmount {str(e)}')
        return {}

async def getTaxOnfloorfeaturesIds(floorFeaturesId):
    try:
        url = f"{os.getenv('SLOT_SERVICE_URL')}/floorfeatures?featuresIds={floorFeaturesId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:            
            return response['response']
        return ""


    except Exception as e:
        print(f'error in getTaxOnfloorfeaturesId {str(e)}')
        return {}

async def getTaxOnpriceId(priceId):
    try:
        url = f"{os.getenv('SLOT_SERVICE_URL')}/priceMaster?priceIds={priceId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:            
            return response['response']
        return ""


    except Exception as e:
        print(f'error in getTaxOnpriceId {str(e)}')
        return {}

async def getPassTransactionTaxId(taxId):
    try:
        response = await routers.client.get(f"{os.getenv('ADMIN_SERVICE_URL')}/taxMaster?taxId={taxId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:            
            return response['response'][0]
        return ""
    except Exception as e:
        print("Exception as getPassTransactionTaxId ",str(e))
        return ""

async def getCancellation(bookingId):
    try:
        url=f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/cancellationRules?bookingId={bookingId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0]['cancellation']
        return ""
    except Exception as e:
        print("Exception as getCancellation ",str(e))
        return ""


async def ExtendedAmtAndTax(floorId,bookingPassId):
    try:
        url=f"{os.getenv('BOOKING_URL')}/booking?floorId={floorId}&bookingId={bookingPassId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:             
                return {
                        'extendAmount':i['extendAmount'],
                        'extendTax':i['extendTax']
                }
        return {
                        'extendAmount':"",
                        'extendTax':""
                }
    except Exception as e:
        print("Exception as ExtendedAmtAndTax ",str(e))
        return ""

async def getfeedbackdetails(bookingId):
    try:
        response = await routers.client.get(f"{os.getenv('USER_SERVICE_URL')}/feedBackMaster?bookingId={bookingId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            if response['statusCode'] == 1:
                for i in response['response']:
                    return [{
                            'FeedbackId':i['FeedbackId'],
                            'parkingOwnerId':i['parkingOwnerId'],
                            'branchId':i['branchId'],
                            'bookingId':i['bookingId'],
                            'feedbackRating':i['feedbackRating'],
                            'feedbackComment':i['feedbackComment'],
                            'userName':i['userName']                            
                        }]
        return []
    except Exception as e:
        print("Exception as getfeedbackdetails ",str(e))
        return {}

async def getExtraFeesFeaturesDetails(bookingId,dic,totalAmount,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT ef.*
                                                FROM extraFees as ef
                                                WHERE ef.bookingPassId = ? AND ef.bookingIdType = 'B'
                                                  FOR JSON PATH) AS  varchar(max))""",(bookingId))
        
        row = await db.fetchone()
        extraFeesRes=[]
        if row[0] != None:
            for i in json.loads(row[0]):
                extraFeesRes.append({'extraFeesId':i['extraFeesId'],'bookingIdType':i['bookingIdType'],'bookingPassId':i['bookingPassId'],'priceId':i.get('priceId'),'count':i['count'],'extraFee':i['extraFee'],'extraFeesDetails':i.get('extraFeesDetails'),'createdDate':i['createdDate'],'createdBy':i['createdBy']})   
            # dic['extraFeesDetail']=extraFeesRes
            response = await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/priceMaster?priceIds={extraFeesRes}")
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                dic['extraFeesTotalAmount']=response['response'][0]['extraFeesAmount']
        await db.execute(f"""SELECT CAST((SELECT ef.*
                                                FROM extraFeatures as ef
                                                WHERE ef.bookingPassId = ? AND ef.bookingIdType = 'B'
                                                  FOR JSON PATH) AS  varchar(max))""",(bookingId))
        
        row = await db.fetchone()
        extraFeaturesRes=[]
        if row[0] != None:
            for i in json.loads(row[0]):
                extraFeaturesRes.append({'extraFeatureId':i['extraFeatureId'],'bookingIdType':i['bookingIdType'],'bookingPassId':i['bookingPassId'],'floorFeaturesId':i['floorFeaturesId'],'count':i['count'],'extraDetail':i.get('extraDetail'),'createdDate':i['createdDate'],'updatedDate':i.get('updatedDate')})

            # dic['extraFeaturesDetail']=extraFeaturesRes
            response = await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/floorfeatures?featuresIds={extraFeaturesRes}")
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                dic['extraFeaturesTotalAmount']=response['response'][0]['extraFeaturesAmount']
                dic['bookingAmount']=totalAmount if totalAmount != None else 0 -(dic['extraFeesTotalAmount']+dic['extraFeaturesTotalAmount'])
    except Exception as e:
        print("Exception as getExtraFeesFeaturesDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }


async def modifiedfloorname(configId,dic):
    dic['FloorName'] = await getConfigMasterNameByConfigId(configId)
    

async def modifiedvehicleconfigdetails(vehicleDetails,dic):
    data = []
    for i in vehicleDetails:

        i.update(await getvehicleconfigmaster(i["vehicleType"]))
        data.append(i)
    dic['vehicleDetails'] = data


async def modifiedfloorfeatures(extraFeaturesDetails,dic):
    data = []
    for i in extraFeaturesDetails:
        i.update(await getfloorfeaturesOnextraFeatureId(i["floorFeaturesId"]))
        data.append(i)
    dic['extraFeaturesDetails']= data


async def modifieduserslotdetails(userSlotDetails,dic):
    data = []
    for i in userSlotDetails:
        i.update(await getvehicleconfigmaster(i["vehicleType"]))
        data.append(i)
    dic['userSlotDetails'] = data

async def modifiedvehicleheader(vehicleType,dic):
    res  = await getvehicleconfigmaster(vehicleType)
    dic.update(res)

async def modifiedbranchDetails(branchId,dic):
    res  = await getbranchDetails(branchId)
    dic['parkingOwnerAddressDetails'] = res


async def modifiedouttimeuserslotdetails(slotDetails,dic):
    data = []
    for i in slotDetails:

        i.update(await getvehicleconfigmaster(i["vehicleType"]))
        data.append(i)
    dic['slotDetails'] = data

async def modifiedparkinglotdetails(userSlotDetails,dic):
    data = []
    for i in userSlotDetails:

        i.update(await getslotdetailsbasedonslot(i["slotId"]))
        data.append(i)
    dic['userSlotDetails'] = data

async def modifiedbranchAddressDetails(branchId,dic):
    res  = await getbranchDetails(branchId)
    dic['branchAddressDetails'] = res

async def modifiedbookingbranchAddressDetails(branchId,dic):
    res  = await getbookingbranchDetails(branchId)
    dic.update (res)


async def modifiedBookinAmount(floorFeaturesId,bookingPassId,dic):
    res  = await getbookingAmount(floorFeaturesId,bookingPassId)
    dic['boookingAmount']=res['boookingAmount']


async def modifiedBookinAmountandTaxAmount(floorFeaturesId,bookingPassId,dic):
    res  = await getbookingAmountandTaxAmount(floorFeaturesId,bookingPassId)
    dic['boookingAmount'],dic['bookingTax']=res['boookingAmount'],res['bookingTax']


async def modifiedcancellation(bookingId,dic):
    dic['cancellation']= await getCancellation(bookingId)

async def modifiedExtendedAmtAndTax(floorId,bookingPassId,dic):
    res  = await ExtendedAmtAndTax(floorId,bookingPassId)
    dic['extendAmount'],dic['extendTax']=res['extendAmount'],res['extendTax']


async def modifiedFeedbackDetails(bookingId, dic):
    res  = await getfeedbackdetails(bookingId)
    dic['feedBackDetails'] = res

    


async def getbookingDetailsBasedOnpaymentStatus(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.paymentStatus=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (paymentStatus))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                                                       
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnpaymentStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnpaymentType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.paymentType=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (paymentType))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnpaymentType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOncancellationStatus(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.cancellationStatus=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (cancellationStatus))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                    
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOncancellationStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnbookingType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.bookingType=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (bookingType))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                    
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnbookingType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnbookingTypeanduserId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.bookingType=? AND bv.userId=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (bookingType,userId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                                                        
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnbookingTypeanduserId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnbookingTypeanduserIdandsubscriptionId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.bookingType=? AND bv.userId=? AND bv.subscriptionId=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (bookingType,userId,subscriptionId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                                                        
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnbookingTypeanduserIdandsubscriptionId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }



async def getbookingDetailsBasedOnbookingDurationType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.bookingDurationType=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (bookingDurationType))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                    
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnbookingDurationType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnbooking(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.booking=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (booking))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                                                        
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnbooking ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnuserId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.userId=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (userId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                    
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnuserId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnfloorId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.floorId=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (floorId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                    
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnfloorId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOncancellationanduserId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.cancellationStatus=? AND bv.userId=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (cancellationStatus,userId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                    
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOncancellationanduserId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnblockId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.blockId=? 
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (blockId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                   
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnblockId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getbookingdetailsonbranchId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.branchId=? 
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (branchId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                    
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingdetailsonbranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnparkingOwnerId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.parkingOwnerId=? 
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (parkingOwnerId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                   
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnparkingOwnerId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnuserIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        if Type == 'H':
            data = []
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.bookingType,bv.branchId,bv.branchName,bv.blockId,bv.blockName,bv.booking,bv.bookingDurationType,bv.floorId,bv.floorName,bv.parkingOwnerId,
                                    bv.parkingName,bv.fromDate,bv.toDate,RIGHT(CONVERT(VARCHAR, bv.fromTime, 100),7) AS fromTime,RIGHT(CONVERT(VARCHAR, bv.toTime, 100),7) AS toTime,bv.accessories,bv.Dates,
                                    bv.phoneNumber,bv.emailId,bv.loginType,bv.offerId,bv.subscriptionId,bv.paidAmount,bv.paymentStatus,bv.paymentType,bv.paymentTypeName,bv.pinNo,bv.refundAmt,bv.refundStatus,
                                    bv.taxAmount,bv.taxId,bv.totalAmount,bv.userId,bv.userName,bv.cancellationCharges,bv.cancellationReason,bv.cancellationStatus,bv.transactionId,bv.bankName,bv.bankReferenceNumber,
                                    bv.walletCash,bv.createdBy,bv.createdDate,bv.updatedBy,bv.updatedDate
                                    ,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                    ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                    ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
                                    FROM bookingView AS bv
                                    WHERE bv.bookingId IN (
									SELECT bookingId 
									FROM booking as b
									INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
									WHERE b.userId=? and vh.bookingIdType = 'B' 
									AND ((b.cancellationStatus = 'Y' OR vh.vehicleStatus='O')
									OR (b.toDate < CONVERT(DATE, GETDATE())))) 
                                    FOR JSON PATH) AS VARCHAR(MAX))
                                """, (userId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await asyncio.gather(modifiedfloorfeatures(dic['extraFeaturesDetails'],dic),
                                         modifiedbookingbranchAddressDetails(dic['branchId'], dic),
                                         modifiedFeedbackDetails(dic['bookingId'],dic))                                      
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnuserIdandType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnbookingId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ef.floorFeaturesId,ef.bookingPassId ,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
                                       FROM bookingView AS bv
                                       INNER JOIN extraFeatures as ef
                                       ON ef.bookingPassId=bv.bookingId
                                       WHERE bv.bookingId=? 
                                       FOR JSON PATH) AS VARCHAR(MAX))
                            """, (bookingId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                                    modifiedfloorfeatures(dic['extraFeaturesDetails'],dic),
                                    modifiedbookingbranchAddressDetails(dic['branchId'], dic),
                                    modifiedparkinglotdetails(dic['userSlotDetails'],dic),
                                    modifiedBookinAmountandTaxAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic)
                                    )
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnbookingId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnuserIdandTypeandfromdateandTodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'H':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.bookingType,bv.branchId,bv.branchName,bv.blockId,bv.blockName,bv.booking,bv.bookingDurationType,bv.floorId,bv.floorName,bv.parkingOwnerId,
                                        bv.parkingName,bv.fromDate,bv.toDate,RIGHT(CONVERT(VARCHAR, bv.fromTime, 100),7) AS fromTime,RIGHT(CONVERT(VARCHAR, bv.toTime, 100),7) AS toTime,bv.accessories,bv.Dates,
                                        bv.phoneNumber,bv.emailId,bv.loginType,bv.offerId,bv.subscriptionId,bv.paidAmount,bv.paymentStatus,bv.paymentType,bv.paymentTypeName,bv.pinNo,bv.refundAmt,bv.refundStatus,
                                        bv.taxAmount,bv.taxId,bv.totalAmount,bv.userId,bv.userName,bv.cancellationCharges,bv.cancellationReason,bv.cancellationStatus,bv.transactionId,bv.bankName,bv.bankReferenceNumber,
                                        bv.walletCash,bv.createdBy,bv.createdDate,bv.updatedBy,bv.updatedDate
                                        ,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									    ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									    ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									    ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
                                        FROM bookingView AS bv
                                        WHERE bv.userId=? AND toDate < GETDATE() AND CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}') 
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (userId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await asyncio.gather(
                                    modifiedfloorfeatures(dic['extraFeaturesDetails'],dic),
                                    modifiedbookingbranchAddressDetails(dic['branchId'], dic))                                        
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnuserIdandTypeandfromdateandTodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getDetailsBasedOnfloorIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'I':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*, bv.pinNo,
                                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                                FROM bookingView AS bv
                                INNER JOIN vehicleHeader AS vh
                                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus IS NULL
                                WHERE bv.floorId=? AND bv.fromDate <= GETDATE()
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """, (floorId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                        
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnfloorIdandType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getDetailsBasedOnfloorIdandTypeandbookingId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'I':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*, bv.pinNo,bv.bookingDurationType,
                                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                                FROM bookingView AS bv
                                INNER JOIN vehicleHeader AS vh
                                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus IS NULL
                                WHERE bv.floorId=? AND bv.bookingId=? AND bv.fromDate <= GETDATE()
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """, (floorId,bookingId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                        
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnfloorIdandTypeandbookingId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getDetailsBasedOnlogintypeandcreatedbyandcreatedDate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							            FROM bookingView AS bv
                                    WHERE bv.loginType=? AND bv.createdBy=? AND bv.createdDate=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (loginType,createdBy,createdDate))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                    
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnlogintypeandcreatedbyandcreatedDate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getDetailsBasedOnlogintypeandcreatedbyandcreatedDateandtype(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='C':
            await db.execute(f"""
                                SELECT CAST((SELECT COUNT(*) AS loginCount
							            FROM bookingView AS bv
                                        WHERE bv.loginType=? AND bv.createdBy=? AND bv.createdDate=?
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (loginType,createdBy,createdDate))
            row = await db.fetchone()
            if row[0] != None:           
                data=(json.loads(row[0]))
                return {
                "response":data,
                "statusCode":1
            }                
            return {
                "response":"data not found",
                "statusCode":0
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnlogintypeandcreatedbyandcreatedDateandtype ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnparkingOwnerIdanduserIdandcancellationstatus(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='C':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
                                        ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                        ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                        ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
                                            FROM bookingView AS bv
                                        WHERE bv.parkingOwnerId=? and bv.userId=? AND bv.cancellationStatus='Y'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (parkingOwnerId,userId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                                                      
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnparkingOwnerIdanduserIdandcancellationstatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnbranchIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='R':
            await db.execute(f"""
                                    SELECT CAST((SELECT * FROM (SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails,
									   (SELECT CASE WHEN bookingDurationType= 'H'
																THEN 
																		DATEDIFF(hour, (SELECT CONVERT(DATETIME, 
																											CONVERT(CHAR(8), GETDATE(), 112) + 
																											' ' + 
																											CONVERT(CHAR(8),CAST(GETDATE() AS time), 108))
																										), 
																							(SELECT CONVERT(DATETIME, 
																												CONVERT(CHAR(8), GETDATE(), 112) + 
																												' ' + 
																												CONVERT(CHAR(8),bv.toTime, 108)
																											)
																							)
																					)
															ELSE 
																DATEDIFF(day,CAST(GETDATE() AS date),bv.toDate)
														END
				
								)AS remainingCount
							FROM bookingView AS bv
							WHERE bv.branchId=? and bv.toDate>=CAST(GETDATE() AS date))as subTab
							WHERE remainingCount >0 FOR JSON PATH) AS VARCHAR(MAX))
                                """, (branchId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await asyncio.gather(modifiedfloorfeatures(dic['extraFeaturesDetails'],dic),
                                         modifiedbranchDetails(dic['branchId'],dic))                                                                               
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnbranchIdandType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnuserIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='E':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
                                        FROM bookingView AS bv
                                        WHERE bv.userId=? AND( (bv.bookingDurationType='H' AND DATEDIFF(day,CAST(GETDATE() AS date),bv.toDate)=1)OR (bv.bookingDurationType='H' AND DATEDIFF(hour, (SELECT CONVERT(DATETIME, 
																											CONVERT(CHAR(8), GETDATE(), 112) + 
																											' ' + 
																											CONVERT(CHAR(8),CAST(GETDATE() AS time), 108))
																										), 
																							(SELECT CONVERT(DATETIME, 
																												CONVERT(CHAR(8), GETDATE(), 112) + 
																												' ' + 
																												CONVERT(CHAR(8),bv.toTime, 108)
																											)
																							)
																					)=1))
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (userId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                        
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnuserIdandType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getDetailsBasedOnfloorIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'I':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*, bv.pinNo
                                FROM bookingView AS bv
                                INNER JOIN vehicleHeader AS vh
                                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus IS NULL
                                WHERE bv.floorId=? AND CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}')
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """, (floorId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                          
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnfloorIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnbranchIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'I':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*, bv.pinNo
                                FROM bookingView AS bv
                                INNER JOIN vehicleHeader AS vh
                                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus IS NULL
                                WHERE bv.branchId=? AND CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}')
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """, (branchId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnbranchIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnblockIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'I':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*, bv.pinNo
                                FROM bookingView AS bv
                                INNER JOIN vehicleHeader AS vh
                                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus IS NULL
                                WHERE bv.blockId=? AND CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}')
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """, (blockId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnblockIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'I':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*, bv.pinNo
                                FROM bookingView AS bv
                                INNER JOIN vehicleHeader AS vh
                                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus IS NULL
                                WHERE bv.parkingOwnerId=? AND CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}')
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """, (parkingOwnerId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'I':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*, bv.pinNo
                                FROM bookingView AS bv
                                INNER JOIN vehicleHeader AS vh
                                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus IS NULL
                                WHERE CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}')
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """)
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getAmountDetailsBasedOnfloorIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 't':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId, ISNULL(bv.totalAmount,0.0)AS totalAmount ,ISNULL(bv.paidAmount,0.0)AS paidAmount,ISNULL((bv.totalAmount-bv.paidAmount),0.0)as RemainingAmount
							    from bookingView bv
                                WHERE bv.floorId=? AND (CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}'))
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """, (floorId))
            row = await db.fetchone()
            if row[0] != None:           
                data=(json.loads(row[0]))
                return {
                "response":data,
                "statusCode":1
            }                
            return {
                "response":"data not found",
                "statusCode":0
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getAmountDetailsBasedOnfloorIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getAmountDetailsBasedOnbranchIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 't':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId, ISNULL(bv.totalAmount,0.0)AS totalAmount ,ISNULL(bv.paidAmount,0.0)AS paidAmount,ISNULL((bv.totalAmount-bv.paidAmount),0.0)as RemainingAmount
							    from bookingView bv
                                WHERE bv.branchId=? AND (CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}'))
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """, (branchId))
            row = await db.fetchone()
            if row[0] != None:           
                data=(json.loads(row[0]))
                return {
                "response":data,
                "statusCode":1
            }                
            return {
                "response":"data not found",
                "statusCode":0
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getAmountDetailsBasedOnbranchIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getAmountDetailsBasedOnblockIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 't':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId, ISNULL(bv.totalAmount,0.0)AS totalAmount ,ISNULL(bv.paidAmount,0.0)AS paidAmount,ISNULL((bv.totalAmount-bv.paidAmount),0.0)as RemainingAmount
							    from bookingView bv
                                WHERE bv.blockId=? AND (CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}'))
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """, (blockId))
            row = await db.fetchone()
            if row[0] != None:           
                data=(json.loads(row[0]))
                return {
                "response":data,
                "statusCode":1
            }                
            return {
                "response":"data not found",
                "statusCode":0
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getAmountDetailsBasedOnblockIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getAmountDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type == 't':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId, ISNULL(bv.totalAmount,0.0)AS totalAmount ,ISNULL(bv.paidAmount,0.0)AS paidAmount,ISNULL((bv.totalAmount-bv.paidAmount),0.0)as RemainingAmount
							    from bookingView bv
                                WHERE bv.parkingOwnerId=? AND (CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}'))
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """, (parkingOwnerId))
            row = await db.fetchone()
            if row[0] != None:           
                data=(json.loads(row[0]))
                return {
                "response":data,
                "statusCode":1
            }                
            return {
                "response":"data not found",
                "statusCode":0
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getAmountDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getAmountDetailsBasedOnTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 't':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId, ISNULL(bv.totalAmount,0.0)AS totalAmount ,ISNULL(bv.paidAmount,0.0)AS paidAmount,ISNULL((bv.totalAmount-bv.paidAmount),0.0)as RemainingAmount
							    from bookingView bv
                                WHERE (CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}'))
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """)
            row = await db.fetchone()
            if row[0] != None:           
                data=(json.loads(row[0]))
                return {
                "response":data,
                "statusCode":1
            }                
            return {
                "response":"data not found",
                "statusCode":0
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getAmountDetailsBasedOnTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }



async def getCountDetailsBasedOnbranchIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type == 'C':
            url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
            slotResponse = await routers.client.get(url)
            slotResponse = json.loads(slotResponse.text)
            slotResp=slotResponse['response']
            url1=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?branchId={branchId}&activeStatus={slotResp}"
            response = await routers.client.get(url1)
            var1 = json.loads(response.text)
            if var1['statusCode']==1:
                for id in var1['response']:
                    await db.execute(f"""
                                        SELECT CAST((SELECT (SELECT COUNT(bookingId) 
                                            FROM booking as b
                                            WHERE CONVERT(date, b.createdDate) = CONVERT(date, GETDATE()) AND b.branchId = ?) AS bookedCount,
                                            (SELECT COUNT(vehicleHeaderId)
                                                FROM booking as b
                                                INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                WHERE vh.bookingIdType='B' AND CONVERT(date, b.createdDate) = CONVERT(date, GETDATE()) AND vh.vehicleStatus = 'I' AND b.branchId = ? ) AS checkedInCount, 
                                            (SELECT COUNT(vehicleHeaderId)
                                                FROM booking as b
                                                INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                WHERE vh.bookingIdType='B' AND CONVERT(date, b.createdDate) = CONVERT(date, GETDATE()) AND vh.vehicleStatus = 'O' AND b.branchId = ? ) AS checkedOutCount,
                                                ({id['totalSlot']})AS available
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                        """, (branchId,branchId,branchId))
                    row = await db.fetchone()
                    if row[0] != None:           
                        data=(json.loads(row[0]))

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getCountDetailsBasedOnbranchIdandType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getCountDetailsBasedOnfloorIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'C':
            url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
            slotResponse = await routers.client.get(url)
            slotResponse = json.loads(slotResponse.text)
            slotResp=slotResponse['response']
            url1=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?floorId={floorId}&activeStatus={slotResp}"
            response = await routers.client.get(url1)
            var1 = json.loads(response.text)
            if var1['statusCode']==1:
                for id in var1['response']:
                    await db.execute(f"""
                                        SELECT CAST((SELECT (SELECT COUNT(bookingId) 
                                            FROM booking as b
                                            WHERE CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}'  AND b.floorId = ?) AS bookedCount,
                                            (SELECT COUNT(vehicleHeaderId)
                                                FROM booking as b
                                                INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                WHERE vh.bookingIdType='B' AND CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}' AND vh.vehicleStatus = 'I' AND b.floorId = ? ) AS checkedInCount, 
                                            (SELECT COUNT(vehicleHeaderId)
                                                FROM booking as b
                                                INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                WHERE vh.bookingIdType='B' AND CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}' AND vh.vehicleStatus = 'O' AND b.floorId = ? ) AS checkedOutCount,
                                                ({id['totalSlot']})AS available
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                        """, (floorId,floorId,floorId))
                    row = await db.fetchone()
                    if row[0] != None:           
                        data=(json.loads(row[0]))

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getCountDetailsBasedOnfloorIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getCountDetailsBasedOnbranchIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'C':
            url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
            slotResponse = await routers.client.get(url)
            slotResponse = json.loads(slotResponse.text)
            slotResp=slotResponse['response']
            url1=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?branchId={branchId}&activeStatus={slotResp}"
            response = await routers.client.get(url1)
            var1 = json.loads(response.text)
            url2=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?branchId={branchId}"
            response = await routers.client.get(url2)
            var2 = json.loads(response.text)
            if var1['statusCode']==1 and var2['statusCode']==1:
                for id in var1['response']:
                    for id1 in var2['response']:
                        await db.execute(f"""
                                            SELECT CAST((SELECT ISNULL((SELECT COUNT(bookingId) 
                                                FROM booking as b
                                                WHERE CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}'  AND b.branchId = ?),0) AS bookedCount,
                                                ISNULL((SELECT COUNT(vehicleHeaderId)
                                                    FROM booking as b
                                                    INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                    WHERE vh.bookingIdType='B' AND CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}'  AND vh.vehicleStatus = 'I' AND b.branchId = ? ),0) AS checkedInCount, 
                                                ISNULL((SELECT COUNT(vehicleHeaderId)
                                                    FROM booking as b
                                                    INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                    WHERE vh.bookingIdType='B' AND CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}'  AND vh.vehicleStatus = 'O' AND b.branchId = ? ),0) AS checkedOutCount,
                                                ISNULL(({id['totalSlot']}),0)AS available,
                                                ISNULL(({id1['COUNT']}),0)AS filled,
                                                ISNULL((SELECT COUNT(vehicleHeaderId)
                                                    FROM booking as b
                                                    INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                    WHERE vh.bookingIdType='P' AND  CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}'  AND vh.vehicleStatus = 'I' AND b.branchId = ? ),0) AS passCheckedIn,
                                                ISNULL((SELECT COUNT(bookingId) 
                                                    FROM booking as b
                                                    WHERE CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}' AND CAST(b.createdDate as date) != '{fromDate}' AND CAST(b.createdDate as date) != '{toDate}' AND b.branchId = ? ),0) AS reserved
                                            FOR JSON PATH) AS VARCHAR(MAX))
                                            """, (branchId,branchId,branchId,branchId,branchId))
                        row = await db.fetchone()
                        if row[0] != None:           
                            data=(json.loads(row[0]))
                if len(data)!=0:
                    return {
                        "response": data,
                        "statusCode":1
                    }
                else:
                    return {
                    "response": "data not found",
                    "statusCode": 0
                }
            return {
                    "response": "data not found",
                    "statusCode": 0
                }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getCountDetailsBasedOnbranchIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getCountDetailsBasedOnblockIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type == 'C':
            url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
            slotResponse = await routers.client.get(url)
            slotResponse = json.loads(slotResponse.text)
            slotResp=slotResponse['response']
            url1=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?blockId={blockId}&activeStatus={slotResp}"
            response = await routers.client.get(url1)
            var1 = json.loads(response.text)
            if var1['statusCode']==1:
                for id in var1['response']:
                    await db.execute(f"""
                                        SELECT CAST((SELECT (SELECT COUNT(bookingId) 
                                            FROM booking as b
                                            WHERE CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}'  AND b.blockId = ?) AS bookedCount,
                                            (SELECT COUNT(vehicleHeaderId)
                                                FROM booking as b
                                                INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                WHERE vh.bookingIdType='B' AND CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}'  AND vh.vehicleStatus = 'I' AND b.blockId = ? ) AS checkedInCount, 
                                            (SELECT COUNT(vehicleHeaderId)
                                                FROM booking as b
                                                INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                WHERE vh.bookingIdType='B' AND CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}'  AND vh.vehicleStatus = 'O' AND b.blockId = ? ) AS checkedOutCount,
                                            ISNULL(({id['totalSlot']}),0)AS available
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                        """, (blockId,blockId,blockId))
                    row = await db.fetchone()
                    if row[0] != None:           
                        data=(json.loads(row[0]))

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getCountDetailsBasedOnblockIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getCountDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type == 'C':
            url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
            slotResponse = await routers.client.get(url)
            slotResponse = json.loads(slotResponse.text)
            slotResp=slotResponse['response']
            url1=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?parkingOwnerId={parkingOwnerId}&activeStatus={slotResp}"
            response = await routers.client.get(url1)
            var1 = json.loads(response.text)
            if var1['statusCode']==1:
                for id in var1['response']:
                    await db.execute(f"""
                                        SELECT CAST((SELECT (SELECT COUNT(bookingId) 
                                            FROM booking as b
                                            WHERE CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}'  AND b.parkingOwnerId = ?) AS bookedCount,
                                            (SELECT COUNT(vehicleHeaderId)
                                                FROM booking as b
                                                INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                WHERE vh.bookingIdType='B' AND CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}' AND vh.vehicleStatus = 'I' AND b.parkingOwnerId = ? ) AS checkedInCount, 
                                            (SELECT COUNT(vehicleHeaderId)
                                                FROM booking as b
                                                INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                WHERE vh.bookingIdType='B' AND CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}' AND vh.vehicleStatus = 'O' AND b.parkingOwnerId = ? ) AS checkedOutCount,
                                            ISNULL(({id['totalSlot']}),0)AS available
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                        """, (parkingOwnerId,parkingOwnerId,parkingOwnerId))
                    row = await db.fetchone()
                    if row[0] != None:           
                        data=(json.loads(row[0]))

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getCountDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getCountDetailsBasedOnTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type == 'C':
            url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
            slotResponse = await routers.client.get(url)
            slotResponse = json.loads(slotResponse.text)
            slotResp=slotResponse['response']
            url1=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?activeStatus={slotResp}"
            response = await routers.client.get(url1)
            var1 = json.loads(response.text)
            if var1['statusCode']==1:
                for id in var1['response']:
                    await db.execute(f"""
                                        SELECT CAST((SELECT (SELECT COUNT(bookingId) 
                                            FROM booking as b
                                            WHERE CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}' ) AS bookedCount,
                                            (SELECT COUNT(vehicleHeaderId)
                                                FROM booking as b
                                                INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                WHERE vh.bookingIdType='B' AND CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}'  AND vh.vehicleStatus = 'I' ) AS checkedInCount, 
                                            (SELECT COUNT(vehicleHeaderId)
                                                FROM booking as b
                                                INNER JOIN vehicleHeader as vh ON vh.bookingPassId = b.bookingId
                                                WHERE vh.bookingIdType='B' AND CAST(b.createdDate as date) between '{fromDate}'  AND '{toDate}'  AND vh.vehicleStatus = 'O' ) AS checkedOutCount,
                                            ISNULL(({id['totalSlot']}),0)AS available
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                        """)
                    row = await db.fetchone()
                    if row[0] != None:           
                        data=(json.loads(row[0]))

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getCountDetailsBasedOnTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getOutimeDetailsBasedOnfloorIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        if Type == 'O':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*,bv.floorId,
                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount,
                    bv.pinNo, ef.floorFeaturesId,
                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                FROM bookingView AS bv
                INNER JOIN vehicleHeader AS vh
                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus='I'
				INNER JOIN extraFeatures AS ef
				ON ef.bookingPassId=bv.bookingId
                WHERE bv.floorId=?  
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """,(floorId))
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data: 
                    await asyncio.gather(modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                        modifiedBookinAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic))                                                                              
                return {
                "response": data,
                "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getOutimeDetailsBasedOnfloorIdandType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }



async def getOuttimeDetailsBasedOnfloorIdandbookingIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        if Type == 'O':                    
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*,bv.floorId,
                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount,
                    bv.pinNo, ef.floorFeaturesId,
                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                FROM bookingView AS bv
                INNER JOIN vehicleHeader AS vh
                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus='I'
				INNER JOIN extraFeatures AS ef
				ON ef.bookingPassId=bv.bookingId
                WHERE  bv.floorId=? and bv.bookingId=? 
                FOR JSON PATH) AS VARCHAR(MAX))
                """,(floorId,bookingId))
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data:
                    await asyncio.gather(modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                          modifiedBookinAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic))                                                                             
                if len(data)!=0:               
                    return {
                    "response": data,
                    "statusCode":1
                    }
                else:
                    return{
                    "response": "data not found",
                    "statusCode": 0   
                    }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getOuttimeDetailsBasedOnfloorIdandbookingIdandType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getOuttimeDetailsBasedOnuserIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        await db.execute(f"""
                                SELECT CAST((SELECT vh.*,bv.floorId,
                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount,
                    bv.pinNo, ef.floorFeaturesId,
                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                FROM bookingView AS bv
                INNER JOIN vehicleHeader AS vh
                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus='I'
				INNER JOIN extraFeatures AS ef
				ON ef.bookingPassId=bv.bookingId
                WHERE bv.userId=?
                FOR JSON PATH) AS VARCHAR(MAX))
                """,(userId))
        row = await db.fetchone()
        if row[0] != None:
            data=json.loads(row[0])                    
            for dic in data:
                await asyncio.gather(modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                        modifiedBookinAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic))                                                                                
            if len(data)!=0:               
                return {
                "response": data,
                "statusCode":1
                }
            else:
                return{
                "response": "data not found",
                "statusCode": 0   
                }
        return {
        "response": "data not found",
        "statusCode": 0
        }
    except Exception as e:
        print("Exception as getOuttimeDetailsBasedOnuserIdandType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getOuttimeDetailsBasedOnfloorIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        if Type == 'O':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*,bv.floorId,
                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount,
                    bv.pinNo, ef.floorFeaturesId,
                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                FROM bookingView AS bv
                INNER JOIN vehicleHeader AS vh
                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus='I'
				INNER JOIN extraFeatures AS ef
				ON ef.bookingPassId=bv.bookingId
                WHERE bv.floorId=? AND CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}')
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """,(floorId))
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data:
                    await asyncio.gather(modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                          modifiedBookinAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic))                                                                                  
                if len(data)!=0:               
                    return {
                    "response": data,
                    "statusCode":1
                    }
                else:
                    return{
                    "response": "data not found",
                    "statusCode": 0   
                    }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getOuttimeDetailsBasedOnfloorIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getOuttimeDetailsBasedOnbranchIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        if Type == 'O':            
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*,bv.floorId,
                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount,
                    bv.pinNo, ef.floorFeaturesId,
                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                FROM bookingView AS bv
                INNER JOIN vehicleHeader AS vh
                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus='I'
				INNER JOIN extraFeatures AS ef
				ON ef.bookingPassId=bv.bookingId
                WHERE bv.branchId=? AND CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}')
                FOR JSON PATH) AS VARCHAR(MAX))
                """,(branchId))
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data:
                    await asyncio.gather(modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                          modifiedBookinAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic))                                                                                
                if len(data)!=0:               
                    return {
                    "response": data,
                    "statusCode":1
                    }
                else:
                    return{
                    "response": "data not found",
                    "statusCode": 0   
                    }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getOuttimeDetailsBasedOnbranchIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getOuttimeDetailsBasedOnblockIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        if Type == 'O':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*,bv.floorId,
                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount,
                    bv.pinNo, ef.floorFeaturesId,
                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                FROM bookingView AS bv
                INNER JOIN vehicleHeader AS vh
                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus='I'
				INNER JOIN extraFeatures AS ef
				ON ef.bookingPassId=bv.bookingId
                WHERE bv.blockId=? AND CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}')
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """,(blockId))
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data:
                    await asyncio.gather(modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                          modifiedBookinAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic))                                                                                  
                if len(data)!=0:               
                    return {
                    "response": data,
                    "statusCode":1
                    }
                else:
                    return{
                    "response": "data not found",
                    "statusCode": 0   
                    }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getOuttimeDetailsBasedOnblockIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getOuttimeDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        if Type == 'O':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*,bv.floorId,
                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount,
                    bv.pinNo, ef.floorFeaturesId,
                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                FROM bookingView AS bv
                INNER JOIN vehicleHeader AS vh
                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus='I'
				INNER JOIN extraFeatures AS ef
				ON ef.bookingPassId=bv.bookingId
                WHERE bv.parkingOwnerId=? AND CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}')
                FOR JSON PATH) AS VARCHAR(MAX))
                """,(parkingOwnerId))
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data:
                    await asyncio.gather(modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                          modifiedBookinAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic))                                                                                
                if len(data)!=0:               
                    return {
                    "response": data,
                    "statusCode":1
                    }
                else:
                    return{
                    "response": "data not found",
                    "statusCode": 0   
                    }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getOuttimeDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getOuttimeDetailsBasedOnTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        if Type == 'O':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*,bv.floorId,
                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount,
                    bv.pinNo, ef.floorFeaturesId,
                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                FROM bookingView AS bv
                INNER JOIN vehicleHeader AS vh
                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus='I'
				INNER JOIN extraFeatures AS ef
				ON ef.bookingPassId=bv.bookingId
                WHERE CAST(bv.createdDate as date) between '{fromDate}'  AND '{toDate}'  OR (CAST(bv.createdDate as date) = '{fromDate}'  AND CAST(bv.createdDate as date) ='{toDate}')
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """)
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data:
                    await asyncio.gather(modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                          modifiedBookinAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic))                                                                                 
                if len(data)!=0:               
                    return {
                    "response": data,
                    "statusCode":1
                    }
                else:
                    return{
                    "response": "data not found",
                    "statusCode": 0   
                    }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getOuttimeDetailsBasedOnTypeandfromdateandtodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getBranchCountBasedOnType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type == 'CB':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.branchId,ISNULL(bv.branchname,'')AS branchname, COUNT(bv.totalAmount) AS totalAmountcount,COUNT(bv.paidAmount) AS paidAmountcount,ISNULL(COUNT(bv.totalAmount-bv.paidAmount),0.0)as RemainingAmountCount
                                    FROM bookingView as bv
                                    GROUP BY bv.totalAmount,bv.paidAmount,bv.branchId,bv.branchname
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """)
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getBranchCountBasedOnType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getParkingCountBasedOnType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type == 'CP':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.parkingOwnerId,ISNULL(bv.parkingName,'')AS parkingName, COUNT(bv.totalAmount) AS totalAmountcount,COUNT(bv.paidAmount) AS paidAmountcount,ISNULL(COUNT(bv.totalAmount-bv.paidAmount),0.0)as RemainingAmountCount
                                    FROM bookingView as bv
                                    GROUP BY bv.totalAmount,bv.paidAmount,bv.parkingOwnerId,bv.parkingName
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """)
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getParkingCountBasedOnType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }



async def getextrafeaturesCountBasedOnbranchIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type == 'FC':
            url2 = f"{os.getenv('SLOT_SERVICE_URL')}/floorfeatures?branchId={branchId}"
            response2 = await routers.client.get(url2)
            var2= json.loads(response2.text)
            if var2['statusCode']==1:
                for id in var2['response'] :
                    await db.execute(f"""
                                        SELECT CAST((SELECT SUM({id['totalAmount']}*ef.count) as totalamount ,SUM({id['tax']}*ef.count) as tax , SUM({id['amount']}*ef.count) as amount
                                        FROM bookingView as bv
                                        INNER JOIN extraFeatures as ef
                                        ON ef.bookingPassId=bv.bookingId
                                        WHERE bv.branchId=?
                                        GROUP BY ef.count    
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                        """,(branchId))
                    row = await db.fetchone()
                    if row[0] != None:           
                        data=(json.loads(row[0]))
                return {
                "response":data,
                "statusCode":1
            }                
            return {
                "response":"data not found",
                "statusCode":0
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getextrafeaturesCountBasedOnbranchIdandType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def CountBasedOnbranchIdandTypeforextrafees(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type == 'EC':
            url2 = f"{os.getenv('SLOT_SERVICE_URL')}/priceMaster?branchId={branchId}&idType=A"
            response2 = await routers.client.get(url2)
            var2= json.loads(response2.text)
            if var2['statusCode']==1:
                for id in var2['response'] :
                    await db.execute(f"""
                                        SELECT CAST((SELECT SUM({id['totalAmount']}*efe.count) as totalamount ,SUM({id['tax']}*efe.count) as tax , SUM({id['amount']}*efe.count) as amount
                                        FROM bookingView as bv
                                        INNER JOIN extraFees as efe
							            ON efe.bookingPassId=bv.bookingId
                                        WHERE bv.branchId=?
                                        GROUP BY efe.count    
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                        """,branchId)
                    row = await db.fetchone()
                    if row[0] != None:           
                        data=(json.loads(row[0]))
                return {
                "response":data,
                "statusCode":1
            }                
            return {
                "response":"data not found",
                "statusCode":0
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as CountBasedOnbranchIdandTypeforextrafees ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }



async def getbookingDetailsbasedonbookingIdorpinnoorvehiclenumber(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""DECLARE @tempVar VARCHAR(10);
                                BEGIN TRY
                                    SET @tempVar=CAST(? AS int)
                                END TRY
                                BEGIN CATCH
                                    SET @tempVar=-1
                                END CATCH
                                SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                                THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                            WHEN CAST(GETDATE() as time) > bv.toTime
                                                THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                            ELSE
                                                NULL
                                        END), '')AS extendDayHour,
                                (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                                ISNULL(bv.totalAmount,0) as initialAmount,
                                ef.floorFeaturesId,vh.bookingPassId,
                            ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                            FROM bookingView AS bv
                            LEFT JOIN vehicleHeader AS vh
                            ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus='I'
                            INNER JOIN extraFeatures AS ef
                            ON ef.bookingPassId=bv.bookingId
                            WHERE (bv.bookingId=@tempVar OR vh.vehicleNumber=? OR bv.pinNo=?)
                            FOR JSON PATH) AS VARCHAR(MAX))
                            """,(inOutDetails,inOutDetails,inOutDetails))
        row = await db.fetchone()
        print('row',row)
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                        modifiedfloorfeatures(dic['extraFeaturesDetails'],dic),
                                        getExtraFeesFeaturesDetails(dic['bookingId'],dic,dic.get('totalAmount'),db) )                                                                                                           
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsbasedonbookingIdorpinnoorvehiclenumber ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getDetailsBasedOnfloorIdandTypeandvehiclenumberandbookingId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type == 'I':
            await db.execute(f"""EXEC [dbo].[getvehicleheaderdetailsbaseonfloorIdbookingvehicleNumber] ?,?
                                """, (inOutDetails,floorId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnfloorIdandTypeandvehiclenumberandbookingId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingBasedOnuserIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        if Type=='R':
            await db.execute(f"""
                                    SELECT CAST((SELECT bv.bookingId,bv.bookingType,bv.branchId,bv.branchName,bv.blockId,bv.blockName,bv.booking,bv.bookingDurationType,bv.floorId,bv.floorName,bv.parkingOwnerId,
                                    bv.parkingName,bv.fromDate,bv.toDate,RIGHT(CONVERT(VARCHAR, bv.fromTime, 100),7) AS fromTime,RIGHT(CONVERT(VARCHAR, bv.toTime, 100),7) AS toTime,bv.accessories,bv.Dates,
                                    bv.phoneNumber,bv.emailId,bv.loginType,bv.offerId,bv.subscriptionId,bv.paidAmount,bv.paymentStatus,bv.paymentType,bv.paymentTypeName,bv.pinNo,bv.refundAmt,bv.refundStatus,
                                    bv.taxAmount,bv.taxId,bv.totalAmount,bv.userId,bv.userName,bv.cancellationCharges,bv.cancellationReason,bv.cancellationStatus,bv.transactionId,bv.bankName,bv.bankReferenceNumber,
                                    bv.walletCash,bv.createdBy,bv.createdDate,bv.updatedBy,bv.updatedDate
                                    ,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId AND vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
                                    ISNULL((SELECT ef.* FROM extraFeatures AS ef  WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                    ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                    ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails,
                                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                            THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'day')
                                        WHEN CAST(GETDATE() as time) > bv.toTime
                                            THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'hour')
                                        ELSE
                                            NULL
                                    END),0)AS remainingCount                                    
                            FROM bookingView AS bv
                            WHERE bv.userId=? and bv.toDate>=CAST(GETDATE() AS date) FOR JSON PATH) AS VARCHAR(MAX))
                                """, (userId))
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data:
                    await asyncio.gather(modifiedfloorfeatures(dic['extraFeaturesDetails'],dic),
                                         modifiedbookingbranchAddressDetails(dic['branchId'], dic),
                                          modifiedcancellation (dic['bookingId'],dic))                                        
                return {
                    "response": data,
                    "statusCode":1
                }
            else:
                return {
                "response": "data not found",
                "statusCode": 0
                }   
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingBasedOnuserIdandType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getOuttimeBasedOnfloorIdandbookingIdandvehiclenumberandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'O':
            await db.execute(f"""DECLARE @tempVar VARCHAR(10);
                                BEGIN TRY
                                    SET @tempVar=CAST(? AS int)
                                END TRY
                                BEGIN CATCH
                                    SET @tempVar=-1
                                END CATCH
                                SELECT CAST((SELECT vh.*,bv.floorId,
                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount,
                    bv.pinNo, ef.floorFeaturesId,
                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                FROM bookingView AS bv
                INNER JOIN vehicleHeader AS vh
                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus='I'
                INNER JOIN extraFeatures as ef ON ef.bookingPassId=bv.bookingId
                WHERE  bv.floorId=? and (bv.bookingId=@tempVar OR vh.vehicleNumber=?)
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """,(inOutDetails,floorId,inOutDetails))
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data:
                    await asyncio.gather(modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                          modifiedBookinAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic))                                                                                 
                if len(data)!=0:               
                    return {
                    "response": data,
                    "statusCode":1
                    }
                else:
                    return{
                    "response": "data not found",
                    "statusCode": 0   
                    }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getOuttimeBasedOnfloorIdandbookingIdandvehiclenumberandType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def DetailsBasedOnfloorIdandTypeandNumber(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'I':
            await db.execute(f"""
                                SELECT CAST((SELECT vh.*, bv.pinNo,
                                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as slotDetails
                                FROM bookingView AS bv
                                INNER JOIN vehicleHeader AS vh
                                ON vh.bookingPassId=bv.bookingId AND vh.vehicleStatus IS NULL
                                WHERE bv.floorId=? AND bv.fromDate <= GETDATE() 
                                ORDER BY vh.vehicleHeaderId
                                OFFSET 10 * ? ROWS
                                FETCH NEXT 10 ROWS ONLY
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """, (floorId,number))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print(f'error {str(e)}')
        return {
            "response": str(e),
            "statusCode": 0
        }

async def getbookingDetailsBasedOnslotId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,vh.bookingPassId,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.bookingIdType = 'B' and vh.slotId=? FOR JSON PATH),'[]') AS vehicleDetails,
                                    ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                    ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount,ef.floorFeaturesId,
                    ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as userSlotDetails	   
                    FROM bookingView AS bv
                    INNER JOIN userSlot as us ON us.bookingPassId = bv.bookingId AND us.bookingIdType = 'B'
                    INNER JOIN vehicleHeader AS vh
                    ON vh.bookingPassId=bv.bookingId
                    INNER JOIN extraFeatures as ef ON ef.bookingPassId=bv.bookingId
                    WHERE us.slotId = ?
                    AND (GETDATE() BETWEEN (CONVERT(DATETIME, CONVERT(CHAR(8), bv.fromDate, 112) + ' ' + CONVERT(CHAR(8), bv.fromTime, 108))) AND (CONVERT(DATETIME, CONVERT(CHAR(8), bv.toDate, 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))))  
                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (slotId,slotId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(modifiedfloorfeatures(dic['extraFeaturesDetails'],dic),
                                    modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                    modifiedBookinAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic))                                                                       
                data.append(dic)
            if len(data)!=0:
                return {
                    "response": data,
                    "statusCode":1
                }
            else:
                return {
                "response": "data not found",
                "statusCode": 0
                 }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnslotId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getbookingDetailsBasedOnPhoneNumber(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId AND vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
                                    ISNULL((SELECT ef.* FROM extraFeatures AS ef  WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                    ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                    ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
							        FROM bookingView AS bv
                                    WHERE bv.phoneNumber=?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (phoneNumber))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                                                       
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnpaymentStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getOuttimeBasedOnInOutDetailsAndType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'P':
            await db.execute(f"""DECLARE @tempVar VARCHAR(10);
                                BEGIN TRY
                                    SET @tempVar=CAST(? AS int)
                                END TRY
                                BEGIN CATCH
                                    SET @tempVar=-1
                                END CATCH
                                SELECT CAST((SELECT vh.*,bv.floorId,
                    ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount,
                    bv.pinNo,ef.floorFeaturesId,bv.bookingDurationType,
                ISNULL((SELECT * FROM userSlot WHERE bookingPassId = bv.bookingId AND bookingIdType='B' FOR JSON PATH), '[]') as userSlotDetails,
                ISNULL((select ef.* from extraFeatures as ef where ef.bookingIdType='B' and ef.bookingPassId=bv.bookingId FOR JSON PATH), '[]') as extraFeaturesDetail,
                ISNULL((select exf.* from extraFees as exf where exf.bookingIdType='B' and exf.bookingPassId=bv.bookingId FOR JSON PATH), '[]') as extraFeesDetail,
                ISNULL((SELECT DATEDIFF(MINUTE,vh.inTime,getdate()) AS DateDiff from vehicleHeader as vh where vh.bookingPassId=bv.bookingId), 0) as vehicleParkedTime
                FROM bookingView AS bv
                INNER JOIN vehicleHeader AS vh
                ON vh.bookingPassId=bv.bookingId AND vh.bookingIdType = 'B' AND (vh.vehicleStatus != 'O' OR vh.vehicleStatus IS NULL)
                INNER JOIN extraFeatures as ef ON ef.bookingPassId=bv.bookingId
                WHERE (vh.vehicleNumber=? OR bv.phoneNumber=? OR bv.emailId=? OR bookingId=@tempVar)
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """,(inOutDetails,inOutDetails,inOutDetails,inOutDetails))
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data:
                    await asyncio.gather(modifiedparkinglotdetails(dic['userSlotDetails'],dic),
                                            modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic),
                                            modifiedBookinAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic))                                                                          
                if len(data)!=0:               
                    return {
                    "response": data,
                    "statusCode":1
                    }
                else:
                    return{
                    "response": "data not found",
                    "statusCode": 0   
                    }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getOuttimeBasedOnInOutDetailsAndType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetailsBasedOnInOutDetailsAndType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type == 'PW':
            await db.execute(f"""
                                SELECT CAST((SELECT TOP 1 bv.bookingId,bv.bookingType,bv.branchId,bv.branchName,bv.blockId,bv.blockName,bv.booking,bv.bookingDurationType,bv.floorId,bv.floorName,bv.parkingOwnerId,
                                        bv.parkingName,bv.fromDate,bv.toDate,RIGHT(CONVERT(VARCHAR, bv.fromTime, 100),7) AS fromTime,RIGHT(CONVERT(VARCHAR, bv.toTime, 100),7) AS toTime,bv.accessories,bv.Dates,
                                        bv.phoneNumber,bv.emailId,bv.loginType,bv.offerId,bv.subscriptionId,bv.paidAmount,bv.paymentStatus,bv.paymentType,bv.paymentTypeName,bv.pinNo,bv.refundAmt,bv.refundStatus,
                                        bv.taxAmount,bv.taxId,bv.totalAmount,bv.userId,ISNULL(bv.userName,'')As userName,bv.cancellationCharges,bv.cancellationReason,bv.cancellationStatus,bv.transactionId,bv.bankName,bv.bankReferenceNumber,
                                        bv.walletCash,bv.createdBy,bv.createdDate,bv.updatedBy,bv.updatedDate
                                        ,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId AND vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
                                        ISNULL((SELECT ef.* FROM extraFeatures AS ef  WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                        ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                        ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
                                        FROM bookingView AS bv
                                        INNER JOIN vehicleHeader AS vh
                                        ON vh.bookingPassId=bv.bookingId AND vh.bookingIdType = 'B' AND (vh.vehicleStatus != 'O' OR vh.vehicleStatus IS NULL)
                                        WHERE (vh.vehicleNumber=? OR bv.phoneNumber=? OR bv.emailId = ? )
                                        ORDER BY bv.bookingId DESC
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (inOutDetails,inOutDetails,inOutDetails))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                                                       
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnpaymentStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def branchIdTypeVFromdateTodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'V':
            url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType&configName=VIP"
            slotResponse = await routers.client.get(url)
            slotResponse = json.loads(slotResponse.text)
            slotResp=slotResponse['response']
            url1=f"{os.getenv('SLOT_SERVICE_URL')}/parkingSlot?branchId={branchId}&activeStatus={slotResp[0]['configId']}&Type=V"
            response = await routers.client.get(url1)
            var1 = json.loads(response.text)
            if var1['statusCode']==1:
                for id in var1['response']:
                    await db.execute(f"""
                                        SELECT CAST((SELECT * FROM (SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId AND vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
                                        ISNULL((SELECT ef.* FROM extraFeatures AS ef  WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                        ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                        ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
                                       FROM bookingView AS bv
                                       INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                       INNER JOIN userSLot as us ON us.bookingPassId = bv.bookingId AND us.bookingIdType='B'							 
						               WHERE bv.branchId=? AND us.slotId = {id['parkingSlotId']}
                                       AND (vhm.inTime BETWEEN '{fromDate}' AND '{toDate}') and vhm.vehicleStatus='I')as A WHERE  userSlotDetails!='[]' 
                                       FOR JSON PATH) AS VARCHAR(MAX))
                                        """, (branchId,))
                    row = await db.fetchone()
                    if row[0] != None:           
                        data=(json.loads(row[0]))
                        for dic in data:
                            await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)
                if len(data)!=0:
                    return {
                        "response": data,
                        "statusCode":1
                    }
                else:
                    return {
                    "response": "data not found",
                    "statusCode": 0
                    }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as branchIdTypeVFromdateTodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def branchIdTypeNFromdateTodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type == 'N':
            url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType&configName=Normal"
            slotResponse = await routers.client.get(url)
            slotResponse = json.loads(slotResponse.text)
            slotResp=slotResponse['response']
            url1=f"{os.getenv('SLOT_SERVICE_URL')}/parkingSlot?branchId={branchId}&activeStatus={slotResp[0]['configId']}&Type=V"
            response = await routers.client.get(url1)
            var1 = json.loads(response.text)
            if var1['statusCode']==1:
                for id in var1['response']:
                    await db.execute(f"""
                                        SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId AND vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
                                        ISNULL((SELECT ef.* FROM extraFeatures AS ef  WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                        ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                        ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
                                       FROM bookingView AS bv
                                       INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                       INNER JOIN userSLot as us ON us.bookingPassId = bv.bookingId 							 
						               WHERE bv.branchId=? AND us.slotId = {id['parkingSlotId']}
                                       AND (vhm.inTime BETWEEN '{fromDate}' AND '{toDate}') and vhm.vehicleStatus='I' 
                                       FOR JSON PATH) AS VARCHAR(MAX))
                                        """, (branchId,))
                    row = await db.fetchone()
                    if row[0] != None:           
                        data=(json.loads(row[0]))
                        for dic in data:
                            await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)
                if len(data)!=0:
                    return {
                        "response": data,
                        "statusCode":1
                    }
                else:
                    return {
                    "response": "data not found",
                    "statusCode": 0
                    }

            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as branchIdTypeNFromdateTodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }




async def detailsbasedonfloorIdandtypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'C':
        res  = await getCountDetailsBasedOnfloorIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res       
    elif Type == 'I':
        res1 = await getDetailsBasedOnfloorIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1       
    elif Type == 't':
        res2 = await getAmountDetailsBasedOnfloorIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res2     
    elif Type == 'O':
        res3 = await getOuttimeDetailsBasedOnfloorIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res3
        


async def branchIdandtypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'I':
        res  = await getDetailsBasedOnbranchIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res  
    elif Type == 't':
        res1 = await getAmountDetailsBasedOnbranchIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1  
    elif Type == 'C':
        res2 = await getCountDetailsBasedOnbranchIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res2   
    elif Type == 'O':
        res3 = await getOuttimeDetailsBasedOnbranchIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res3
    elif Type == 'CU':
        res4 = await getDetailsBasedOnbranchIdAndTypeCU(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res4
    elif Type == 'CI':
        res5 = await getDetailsBasedOnbranchIdAndTypeCI(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res5
    elif Type == 'CO':
        res6 = await getDetailsBasedOnbranchIdAndTypeCO(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res6
    elif Type == 'V':
        res7 = await branchIdTypeVFromdateTodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res7
    elif Type == 'N':
        res8 = await branchIdTypeNFromdateTodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res8
    elif Type == 'RE':
        res9 = await getDetailsBasedOnBranchIdAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res9


async def blockIdandtypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'C':
        res = await getCountDetailsBasedOnblockIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res
    elif Type == 'I':
        res1 = await getDetailsBasedOnblockIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1
    elif Type == 't':
        res2 = await getAmountDetailsBasedOnblockIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res2
    elif Type == 'O':
        res3 = await getOuttimeDetailsBasedOnblockIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res3


async def parkingOwnerIdandtypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'C':
        res = await getCountDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res
    elif Type == 'I':
        res1 = await getDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1
    elif Type == 't':
        res2 = await getAmountDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res2
    elif Type == 'O':
        res3 = await getOuttimeDetailsBasedOnparkingOwnerIdandTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res3


async def typeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'C':
        res = await getCountDetailsBasedOnTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res
    elif Type == 'I':
        res1 = await getDetailsBasedOnTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1
    elif Type == 't':
        res2 = await getAmountDetailsBasedOnTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res2
    elif Type == 'O':
        res3 = await getOuttimeDetailsBasedOnTypeandfromdateandtodate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res3

async def userIdandtype (branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'H':
        res = await getbookingDetailsBasedOnuserIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res
    elif Type == 'O':
        res1 = await getOuttimeDetailsBasedOnuserIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1
    elif Type == 'E':
        res2 = await getDetailsBasedOnuserIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res2
    elif Type == 'R':
        res3 = await getbookingBasedOnuserIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res3

async def floorIdandType (branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'I':
        res = await getDetailsBasedOnfloorIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res
    elif Type == 'O':
        res1 = await getOutimeDetailsBasedOnfloorIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1

async def floorIdandbookingIdandType (branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'I':
        res = await getDetailsBasedOnfloorIdandTypeandbookingId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res
    elif Type == 'O':
        res1 = await getOuttimeDetailsBasedOnfloorIdandbookingIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1

async def branchIdandType (branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'R':
        res = await getDetailsBasedOnbranchIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res
    elif Type == 'C':
        res1 = await getCountDetailsBasedOnbranchIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1
    elif Type == 'FC':
        res2 = await getextrafeaturesCountBasedOnbranchIdandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res2
    elif Type == 'EC':
        res3 = await CountBasedOnbranchIdandTypeforextrafees(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res3


async def detailsbasedontype (branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'CB':
        res = await getBranchCountBasedOnType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res
    elif Type == 'CP':
        res1 = await getParkingCountBasedOnType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1


async def detailsbasedontypeandfloorandvehiclenumberorbookingId (branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'I':
        res = await getDetailsBasedOnfloorIdandTypeandvehiclenumberandbookingId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res
    elif Type == 'O':
        res1 = await getOuttimeBasedOnfloorIdandbookingIdandvehiclenumberandType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1

async def detailsBasedOnTypeandInOutDetails (branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    if Type == 'P':
        res = await getOuttimeBasedOnInOutDetailsAndType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res
    elif Type == 'PW':
        res1 = await getbookingDetailsBasedOnInOutDetailsAndType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db)
        return res1        
    
async def getBookingDetailsBasedOnDateTime(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT branchId, us.slotId 
                                            FROM booking as b
                                            INNER JOIN userSlot as us 
                                            ON us.bookingPassId = b.bookingId AND us.bookingIdType = 'B'
                                            WHERE (CONVERT(DATETIME, CONVERT(CHAR(8), b.fromDate, 112) + ' ' + CONVERT(CHAR(8), b.fromTime, 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108))
												OR CONVERT(DATETIME, CONVERT(CHAR(8), b.toDate, 112) + ' ' + CONVERT(CHAR(8), b.toTime, 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108))
												OR CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), b.fromDate, 112) + ' ' + CONVERT(CHAR(8), b.fromTime, 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8), b.toDate, 112) + ' ' + CONVERT(CHAR(8), b.toTime, 108))
												OR CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), b.fromDate, 112) + ' ' + CONVERT(CHAR(8), b.fromTime, 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8), b.toDate, 112) + ' ' + CONVERT(CHAR(8), b.toTime, 108)))
                                            GROUP BY branchId, us.slotId
                                            FOR JSON AUTO) AS  varchar(max))""",(fromDate,fromTime,toDate,toTime,fromDate,fromTime,toDate,toTime,fromDate,fromTime,toDate,toTime))
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
        print("Exception as getBookingDetailsBasedOnDateTime",str(e))
        return{"statusCode":0,"response":"Server Error"}

async def getBookingDetailsBasedOnDateTimeCategory(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ISNULL(COUNT(vh.vehicleHeaderId),0) AS slotCapacity 
                                            FROM booking as b 
											INNER JOIN vehicleHeader as vh 
                                            ON b.bookingId = vh.bookingPassId AND vh.bookingIdType='B'
                                            WHERE (CONVERT(DATETIME, CONVERT(CHAR(8), b.fromDate, 112) + ' ' + CONVERT(CHAR(8), b.fromTime, 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108))
												OR CONVERT(DATETIME, CONVERT(CHAR(8), b.toDate, 112) + ' ' + CONVERT(CHAR(8), b.toTime, 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108))
												OR CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), b.fromDate, 112) + ' ' + CONVERT(CHAR(8), b.fromTime, 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8), b.toDate, 112) + ' ' + CONVERT(CHAR(8), b.toTime, 108))
												OR CONVERT(DATETIME, CONVERT(CHAR(8), ?, 112) + ' ' + CONVERT(CHAR(8), ?, 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), b.fromDate, 112) + ' ' + CONVERT(CHAR(8), b.fromTime, 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8), b.toDate, 112) + ' ' + CONVERT(CHAR(8), b.toTime, 108)))
                                                AND b.branchId = ?
												AND vh.vehicleType = ?
                                            FOR JSON AUTO) AS  varchar(max))""",(fromDate,fromTime,toDate,toTime,fromDate,fromTime,toDate,toTime,fromDate,fromTime,toDate,toTime,branchId,category))
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
        print("Exception as getBookingDetailsBasedOnDateTimeCategory",str(e))
        return{"statusCode":0,"response":"Server Error"}

async def getDetailsBasedOnbranchIdAndTypeCU(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type=='CU':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId AND vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
                                    ISNULL((SELECT ef.* FROM extraFeatures AS ef  WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                    ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                    ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
                                            FROM bookingView AS bv
                                        INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                        WHERE bv.branchId=?  
                                        AND (bv.fromDate BETWEEN '{fromDate}' AND '{toDate}')
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (branchId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                                                       
                    data.append(dic)

                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnbranchIdAndTypeCU ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnbranchIdAndTypeCI(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type=='CI':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId AND vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
                                    ISNULL((SELECT ef.* FROM extraFeatures AS ef  WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                    ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                    ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
                                            FROM bookingView AS bv
                                        INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                        WHERE bv.branchId=?  
                                        AND (vhm.inTime BETWEEN '{fromDate}' AND '{toDate}')
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (branchId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                                                       
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnbranchIdAndTypeCI ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnbranchIdAndTypeCO(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        if Type=='CO':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId AND vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
                                    ISNULL((SELECT ef.* FROM extraFeatures AS ef  WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                    ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                    ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails
                                            FROM bookingView AS bv
                                        INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                        WHERE bv.branchId=?  
                                        AND (vhm.outTime BETWEEN '{fromDate}' AND '{toDate}')
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (branchId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await modifiedfloorfeatures(dic['extraFeaturesDetails'],dic)                                                                       
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnbranchIdAndTypeCO ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnPaymentTypeAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.paymentType=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (paymentType))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnPaymentTypeAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBookingAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.booking=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (booking))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBookingAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBookingPaymentTypeAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.booking=? AND bv.paymentType=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (booking,paymentType))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBookingPaymentTypeAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBookingPaymentUserIdTypeAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.booking=? AND bv.paymentType=? AND vhm.updatedBy=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (booking,paymentType,userId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBookingPaymentUserIdTypeAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBookingPaymentCategoryTypeAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.booking=? AND bv.paymentType=? AND vhm.vehicleType=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (booking,paymentType,category))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBookingPaymentCategoryTypeAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBookingPaymentCategoryUserIdAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.booking=? AND bv.paymentType=? AND vhm.vehicleType=? AND vhm.updatedBy=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (booking,paymentType,category,userId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBookingPaymentCategoryUserIdAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.branchId=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (branchId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdPaymentTypeAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.paymentType=? and bv.branchId=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (paymentType,branchId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdPaymentTypeAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdBookingAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.booking=? and bv.branchId=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (booking,branchId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdBookingAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdBookingPaymentTypeAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.booking=? and bv.paymentType=? and bv.branchId=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (booking,paymentType,branchId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdBookingPaymentTypeAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdBookingPaymentTypeUserIdAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.booking=? and bv.paymentType=? and bv.branchId=? and vhm.updatedBy=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (booking,paymentType,branchId,userId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdBookingPaymentTypeUserIdAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdBookingcategoryAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.booking=? and bv.branchId=? and vhm.vehicleType=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (booking,branchId,category))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdBookingcategoryAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdBookingPaymentTypecategoryAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.booking=? and bv.paymentType=? and bv.branchId=? and vhm.vehicleType=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (booking,paymentType,branchId,category))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdBookingPaymentTypecategoryAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdBookingPaymentTypecategoryUserIdAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.booking=? and bv.paymentType=? and bv.branchId=? and vhm.vehicleType=? and vhm.updatedBy=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (booking,paymentType,branchId,category,userId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdBookingPaymentTypecategoryUserIdAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getDetailsBasedOnBranchIdPaymentTypUserIdAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE bv.paymentType=? and bv.branchId=? and vhm.updatedBy=?
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (paymentType,branchId,userId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdPaymentTypUserIdAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdPaymentTypecategoryAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE  bv.paymentType=? and bv.branchId=? and vhm.vehicleType=? 
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (paymentType,branchId,category))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdPaymentTypecategoryAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdPaymentTypecategoryUserIdAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE  bv.paymentType=? and bv.branchId=? and vhm.vehicleType=? and vhm.updatedBy=? 
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (paymentType,branchId,category,userId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdPaymentTypecategoryUserIdAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdcategoryAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE  bv.branchId=? and vhm.vehicleType=?  
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (branchId,category))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdcategoryAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdUserIdAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE  bv.branchId=? and vhm.updatedBy=?  
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (branchId,userId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdUserIdAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getDetailsBasedOnBranchIdUserIdCategoryAndTypeRE(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        if Type=='RE':
            await db.execute(f"""
                                SELECT CAST((SELECT bv.bookingId,bv.booking,bv.paymentType,bv.userId,(vhm.vehicleType)AS category,bv.paymentTypeName,ISNULL(bv.userName,'')AS userName,(vhm.vehicleTypeName)As categoryName,bv.branchId,ISNULL(bv.branchName,'')As branchName,
                                            ISNULL((CASE WHEN EXISTS(SELECT * FROM paymentTransactionHistory as pt
                                                INNER JOIN booking as bv ON bv.bookingId=pt.bookingId
                                                WHERE CAST(pt.createdDate as date) BETWEEN CAST('{fromDate}' as date) and CAST('{toDate}' as date) and (bv.booking='PA' OR bv.booking='PW')) 
                                            THEN
                                                (SELECT(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='D' and bookingId=bv.bookingId )-(SELECT ISNULL((SUM(amount)),0)as amount FROM paymentTransactionHistory WHERE amountType='C' and bookingId=bv.bookingId)As Amount)
                                            ELSE
                                                bv.paidAmount
                                            END),0)AS TotalAmount
                                            ,ISNULL((bv.totalAmount-bv.taxAmount),0.0)as Amount,bv.taxAmount,ISNULL(vhm.outTime,'')As Date FROM bookingView AS bv
                                                    INNER JOIN vehicleHeader as vhm ON vhm.bookingPassId = bv.bookingId AND vhm.bookingIdType='B'
                                                    WHERE  bv.branchId=? and vhm.updatedBy=? and vhm.vehicleType=? 
                                                        AND (CAST(vhm.outTime as date) BETWEEN CAST('{fromDate}' as date) AND CAST('{toDate}' as date)) AND vhm.vehicleStatus='O'
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                """, (branchId,userId,category))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)                                                                      
                    data.append(dic)
                return {
                    "response": data,
                    "statusCode":1
                }
            return {
            "response": "data not found",
            "statusCode": 0
        }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchIdUserIdCategoryAndTypeRE ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getbookingDetails(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId AND vh.bookingIdType = 'B' FOR JSON PATH),'[]') AS vehicleDetails,
                                    ISNULL((SELECT ef.* FROM extraFeatures AS ef  WHERE ef.bookingPassId=bv.bookingId AND ef.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeaturesDetails,
                                    ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId AND exf.bookingIdType='B' FOR JSON PATH),'[]')AS extraFeesDetails,
                                    ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId AND uss.bookingIdType='B' FOR JSON PATH),'[]')AS userSlotDetails                                    
                                    FROM bookingView AS bv
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """)
        row = await db.fetchone()
        if row[0] != None:
            data=json.loads(row[0])                    
            for dic in data:
                await asyncio.gather(modifiedfloorfeatures(dic['extraFeaturesDetails'],dic),
                                     modifiedcancellation (dic['bookingId'],dic))            
            return {
            "response": data,
            "statusCode":1
            } 
        else:
            return{
            "response": "data not found",
            "statusCode": 0   
            }
    except Exception as e:
        print("Exception as getbookingDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getextendedAmountAndTax(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data=[]
        url1 = f"{os.getenv('SLOT_SERVICE_URL')}/priceMaster?floorId={floorId}&timetype=EH&idType=V&activeStatus=A"
        response1 = await routers.client.get(url1)
        var1= json.loads(response1.text)
        url2 = f"{os.getenv('SLOT_SERVICE_URL')}/priceMaster?floorId={floorId}&timetype=ED&idType=V&activeStatus=A"
        response2 = await routers.client.get(url2)
        var2= json.loads(response2.text)
        if var1['statusCode']==1 and var2['statusCode']==1:   
            for id in var1['response'] :
                for id1 in var2['response']:
                    await db.execute(f"""
                                        SELECT CAST((SELECT ISNULL((SELECT CASE WHEN GETDATE()> CONVERT(DATETIME, CONVERT(CHAR(8),cast(bv.toDate as date), 112) + ' ' + CONVERT(CHAR(8),bv.toTime, 108))
											THEN 
											 case When bv.bookingDurationType='D'
												then
													CEILING(CAST (DATEDIFF(minute, (CONVERT(DATETIME, CONVERT(CHAR(8),cast(bv.toDate as date), 112) + ' ' + CONVERT(CHAR(8),bv.toTime, 108))),GETDATE()) AS DECIMAL(10,4)) / (60 * 24))*(SELECT {id1['totalAmount']} WHERE bv.floorId={id1['floorId']} AND ISNULL(({id1['graceTime']}),0)< DATEDIFF(MINUTE, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8),cast(bv.toDate as date), 112) + ' ' + CONVERT(CHAR(8),bv.toTime, 108))), GETDATE()))
                                                when bv.bookingDurationType='H'
                                                then
                                                    CEILING(CAST ( DATEDIFF(minute, (CONVERT(DATETIME, CONVERT(CHAR(8), cast(bv.toDate as date), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))),GETDATE()) AS DECIMAL(10,4))/ 60) *(SELECT {id['totalAmount']} WHERE bv.floorId={id['floorId']}  AND ISNULL(({id['graceTime']}),0)< DATEDIFF(MINUTE, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8),cast(bv.toDate as date), 112) + ' ' + CONVERT(CHAR(8),bv.toTime, 108))), GETDATE()))
                                                end
                                                ELSE
                                                    NULL
                                                END), 0)AS extendAmount,
                                                ISNULL((CASE WHEN GETDATE() > CONVERT(DATETIME, CONVERT(CHAR(8),cast(bv.toDate as date), 112) + ' ' + CONVERT(CHAR(8),bv.toTime, 108))
											    then 
												case When bv.bookingDurationType='D'
													THEN 
													    CEILING(CAST (DATEDIFF(minute, (CONVERT(DATETIME, CONVERT(CHAR(8),cast(bv.toDate as date), 112) + ' ' + CONVERT(CHAR(8),bv.toTime, 108))),GETDATE()) AS DECIMAL(10,4)) / (60 * 24)) *(SELECT {id1['tax']} WHERE bv.floorId={id1['floorId']} AND ISNULL(({id1['graceTime']}),0)< DATEDIFF(MINUTE, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8),cast(bv.toDate as date), 112) + ' ' + CONVERT(CHAR(8),bv.toTime, 108))), GETDATE()))
                                                    when bv.bookingDurationType='H'
					
													THEN 	
													    CEILING(CAST ( DATEDIFF(minute, (CONVERT(DATETIME, CONVERT(CHAR(8), cast(bv.toDate as date), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))),GETDATE()) AS DECIMAL(10,4))/ 60)*(SELECT {id['tax']} WHERE bv.floorId={id['floorId']}  AND ISNULL(({id['graceTime']}),0)< DATEDIFF(MINUTE, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8),cast(bv.toDate as date), 112) + ' ' + CONVERT(CHAR(8),bv.toTime, 108))), GETDATE()))
                                                    END
                                                    ELSE
                                                        NULL
                                                END), 0)AS extendTax
                                                FROM booking AS bv
                                                INNER JOIN vehicleHeader AS vh
                                                ON vh.bookingPassId=bv.bookingId
                                                WHERE vh.bookingPassId=? AND  bv.floorId={id['floorId']} AND bv.floorId={id1['floorId']}
                                                FOR JSON PATH) AS VARCHAR(MAX))
                                        """,(bookingId))
                    row = await db.fetchone()
                    if row[0] != None:
                        data=json.loads(row[0])
            if len(data)!=0:                               
                return {
                "response": data,
                "statusCode":1
                } 
            else:
                return{
                "response": "data not found",
                "statusCode": 0   
                }
        else:
            return{
            "response": "data not found",
            "statusCode": 0   
            }
    except Exception as e:
        print("Exception as getextendedAmountAndTax ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

        
#*********************for parking slot 'Mohan'**************************** start#      

async def getbookingSlotsBasedOnFromTimeToTimeFromDate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((
                                SELECT us.slotId FROM booking as bk INNER JOIN userSlot as us
				ON bk.bookingId=us.bookingPassId
					WHERE (('{fromTime}' BETWEEN bk.fromTime  AND bk.toTime)  OR (bk.fromTime BETWEEN '{fromTime}' AND '{toTime}')) 
					AND (('{toTime}' BETWEEN bk.fromTime  AND bk.toTime) OR (bk.ToTime BETWEEN '{fromTime}' AND '{toTime}'))  
					AND '{fromDate}' between bk.fromDate AND bk.toDate and bk.floorId={floorId}
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """)
        row = await db.fetchone()
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingSlotsBasedOnFromTimeToTimeFromDate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
        
        
async def getbookingSlotsBasedOnFromTimeToTimeFromDateBranchId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((
                                SELECT us.slotId FROM booking as bk INNER JOIN userSlot as us
				ON bk.bookingId=us.bookingPassId
					WHERE (('{fromTime}' BETWEEN bk.fromTime  AND bk.toTime)  OR (bk.fromTime BETWEEN '{fromTime}' AND '{toTime}')) 
					AND (('{toTime}' BETWEEN bk.fromTime  AND bk.toTime) OR (bk.ToTime BETWEEN '{fromTime}' AND '{toTime}'))  
					AND '{fromDate}' between bk.fromDate AND bk.toDate AND bk.branchId=?
                                     FOR JSON PATH) AS VARCHAR(MAX))
                            """,(branchId))
        row = await db.fetchone()
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingSlotsBasedOnFromTimeToTimeFromDateBranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
        
        
async def getbookingSlotsBasedOnFromTimeToTimeFromDateToDateBranchId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((
                                SELECT us.slotId FROM booking as bk INNER JOIN userSlot as us
				ON bk.bookingId=us.bookingPassId
				WHERE (CONVERT(DATETIME, CONVERT(CHAR(8), bk.fromDate, 112) + ' ' + CONVERT(CHAR(8), bk.fromTime, 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), cast('{fromDate}' as Date), 112) + ' ' + CONVERT(CHAR(8),'{fromTime}', 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8),cast('{toDate}' as Date), 112) + ' ' + CONVERT(CHAR(8),'{toTime}', 108))
				OR CONVERT(DATETIME, CONVERT(CHAR(8), bk.toDate, 112) + ' ' + CONVERT(CHAR(8), bk.toTime, 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), cast('{fromDate}' as Date), 112) + ' ' + CONVERT(CHAR(8),'{fromTime}', 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8),cast('{toDate}' as Date), 112) + ' ' + CONVERT(CHAR(8),'{toTime}', 108))
				OR CONVERT(DATETIME, CONVERT(CHAR(8), cast('{fromDate}' as Date), 112) + ' ' + CONVERT(CHAR(8), '{fromTime}', 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), bk.fromDate, 112) + ' ' + CONVERT(CHAR(8), bk.fromTime, 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8), bk.toDate, 112) + ' ' + CONVERT(CHAR(8), bk.toTime, 108))
				OR CONVERT(DATETIME, CONVERT(CHAR(8), cast('{toDate}' as Date), 112) + ' ' + CONVERT(CHAR(8), '{toTime}', 108)) BETWEEN CONVERT(DATETIME, CONVERT(CHAR(8), bk.fromDate, 112) + ' ' + CONVERT(CHAR(8), bk.fromTime, 108))  AND CONVERT(DATETIME, CONVERT(CHAR(8), bk.toDate, 112) + ' ' + CONVERT(CHAR(8), bk.toTime, 108)))
	            and bk.branchId=?
     FOR JSON PATH) AS VARCHAR(MAX))
                            """,(branchId))
        row = await db.fetchone()
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingSlotsBasedOnFromTimeToTimeFromDateToDateBranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
        
async def getbookingSlotsBasedOnFromDateToDateBranchId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
       
        await db.execute(f"""
                            SELECT CAST((
                                SELECT us.slotId FROM booking as bk INNER JOIN userSlot as us
				ON bk.bookingId=us.bookingPassId
				WHERE  (('{fromDate}' BETWEEN bk.fromDate  AND bk.toDate)  OR (bk.fromDate BETWEEN '{fromDate}' AND '{toDate}')) AND (('{toDate}' BETWEEN bk.fromDate  AND bk.toDate) OR (bk.toDate BETWEEN '{fromDate}' AND '{toDate}')) and bk.branchId=?
     FOR JSON PATH) AS VARCHAR(MAX))
                            """,(branchId))
        row = await db.fetchone()
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingSlotsBasedOnFromTimeToTimeFromDateToDateBranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
        

async def getbookingSlotsBasedOnFromTimeToTimeToDate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((
                                SELECT us.slotId FROM booking as bk INNER JOIN userSlot as us
				ON bk.bookingId=us.bookingPassId
					WHERE (('{fromTime}' BETWEEN bk.fromTime  AND bk.toTime)  OR (bk.fromTime BETWEEN '{fromTime}' AND '{toTime}')) 
					AND (('{toTime}' BETWEEN bk.fromTime  AND bk.toTime) OR (bk.ToTime BETWEEN '{fromTime}' AND '{toTime}'))  
					AND '{toDate}' between bk.fromDate AND bk.toDate and bk.floorId={floorId}
                                     FOR JSON PATH) AS VARCHAR(MAX))
                            """)
        row = await db.fetchone()
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingSlotsBasedOnFromTimeToTimeToDate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
        
        

async def getbookingSlotsBasedOnFromDate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((
                                SELECT us.slotId FROM booking as bk INNER JOIN userSlot as us
				ON bk.bookingId=us.bookingPassId
					WHERE '{fromDate}' between bk.fromDate AND bk.toDate and bk.floorId={floorId}
                                     FOR JSON PATH) AS VARCHAR(MAX))
                            """)
        row = await db.fetchone()
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingSlotsBasedOnFromDate ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
        

async def getbookingSlotsBasedOnToDate(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((
                                SELECT us.slotId FROM booking as bk INNER JOIN userSlot as us
				ON bk.bookingId=us.bookingPassId
					WHERE '{toDate}' between bk.fromDate AND bk.toDate and bk.floorId={floorId}
                                     FOR JSON PATH) AS VARCHAR(MAX))
                            """)
        row = await db.fetchone()
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingSlotsBasedOnToDate",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
        
        
async def getbookingSlotsBasedOnFromDateToDatefloorId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((
                                SELECT us.slotId FROM booking as bk INNER JOIN userSlot as us
				ON bk.bookingId=us.bookingPassId
					WHERE (('{fromDate}' BETWEEN bk.fromDate  AND bk.toDate)  OR (bk.fromDate BETWEEN '{fromDate}' AND '{toDate}')) AND (('{toDate}' BETWEEN bk.fromDate AND bk.toDate) OR (bk.ToDate BETWEEN '{fromDate}' AND '{toDate}')) and bk.floorId={floorId}
                                     FOR JSON PATH) AS VARCHAR(MAX))
                            """)
        row = await db.fetchone()
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingSlotsBasedOnToDate",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
        
async def getbookingSlotsBasedOnfloorId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):

    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((
                                SELECT us.slotId FROM booking as bk INNER JOIN userSlot as us
				ON bk.bookingId=us.bookingPassId
					WHERE bk.floorId={floorId}
                                     FOR JSON PATH) AS VARCHAR(MAX))
                            """)
        row = await db.fetchone()
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingSlotsBasedOnToDate",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
        
async def getbookingDetailsBasedOnbookingIdSlotId(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ef.floorFeaturesId,ef.bookingPassId ,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId and vh.slotId='{slotId}' FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId FOR JSON PATH),'[]')AS userSlotDetails,
                                        ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount
                                       FROM bookingView AS bv
                                       INNER JOIN extraFeatures as ef
                                       ON ef.bookingPassId=bv.bookingId
                                       WHERE bv.bookingId=? 
                                       FOR JSON PATH) AS VARCHAR(MAX))
                            """, (bookingId))
        row = await db.fetchone()
        print(row)
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                                    modifiedfloorfeatures(dic['extraFeaturesDetails'],dic),
                                    modifiedbranchAddressDetails(dic['branchId'], dic),
                                    modifiedparkinglotdetails(dic['userSlotDetails'],dic),
                                    modifiedBookinAmountandTaxAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic),
                                    modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic)
                                    )
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnbookingId ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getbookingDetailsBasedOnbookingIdType(branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT bv.*,ef.floorFeaturesId,ef.bookingPassId ,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=bv.bookingId FOR JSON PATH),'[]') AS vehicleDetails,
									   ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=bv.bookingId FOR JSON PATH),'[]')AS extraFeaturesDetails,
									   ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=bv.bookingId FOR JSON PATH),'[]')AS extraFeesDetails,
									   ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=bv.bookingId FOR JSON PATH),'[]')AS userSlotDetails,
                                        ISNULL((SELECT CASE WHEN CAST(GETDATE() as date)>bv.toDate
                                    THEN CONCAT(CAST(DATEDIFF(day,  bv.toDate, CAST(GETDATE() as date)) as varchar(5)),'-day')
                                WHEN CAST(GETDATE() as time) > bv.toTime
                                    THEN CONCAT(CAST(DATEDIFF(hour, (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), bv.toTime, 108))), (SELECT CONVERT(DATETIME, CONVERT(CHAR(8), GETDATE(), 112) + ' ' + CONVERT(CHAR(8), CAST(GETDATE() as time), 108)))) as varchar(5)),'-hour')
                                ELSE
                                    NULL
                            END), '')AS extendDayHour,
                    (ISNULL(bv.totalamount,0) - ISNULL(bv.paidAmount,0)) as remainingAmount,
                    ISNULL(bv.totalAmount,0) as initialAmount
                                       FROM bookingView AS bv
                                       INNER JOIN extraFeatures as ef
                                       ON ef.bookingPassId=bv.bookingId
                                       WHERE bv.bookingId=? 
                                       FOR JSON PATH) AS VARCHAR(MAX))
                            """, (bookingId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                                    modifiedfloorfeatures(dic['extraFeaturesDetails'],dic),
                                    modifiedbranchAddressDetails(dic['branchId'], dic),
                                    modifiedparkinglotdetails(dic['userSlotDetails'],dic),
                                    modifiedBookinAmountandTaxAmount(dic['floorFeaturesId'],dic['bookingPassId'],dic),
                                    modifiedExtendedAmtAndTax(dic['floorId'],dic['bookingPassId'],dic)
                                    )
                data.append(dic)

            return {
                "response": data,
                "statusCode":1
            }
        return {
            "response": "data not found",
            "statusCode": 0
        }
    except Exception as e:
        print("Exception as getbookingDetailsBasedOnbookingIdType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }   

   
#*********************for parking slot 'Mohan'**************************** end# 

bookingDict = {

    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingdetailsonbranchId,
    "branchId=False, paymentStatus=True, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnpaymentStatus,
    "branchId=False, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnpaymentType,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=True, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOncancellationStatus,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=True, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnbookingType,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=True, bookingDurationType=False, booking=False, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnbookingTypeanduserId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=True, bookingDurationType=False, booking=False, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=True, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnbookingTypeanduserIdandsubscriptionId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=True, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnbookingDurationType,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnbooking,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnuserId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=True, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnfloorId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=True, bookingType=False, bookingDurationType=False, booking=False, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOncancellationanduserId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=True, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnblockId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=True, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnparkingOwnerId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=True, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnbookingId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False": userIdandtype,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnuserIdandTypeandfromdateandTodate,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=True, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False": floorIdandType,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=True, blockId=False, parkingOwnerId=False, bookingId=True, Type=True, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":floorIdandbookingIdandType,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=True, createdBy=True, createdDate=True, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnlogintypeandcreatedbyandcreatedDate,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=False, toDate=False, loginType=True, createdBy=True, createdDate=True, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnlogintypeandcreatedbyandcreatedDateandtype,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=True, bookingType=False, bookingDurationType=False, booking=False, userId=True, floorId=False, blockId=False, parkingOwnerId=True, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnparkingOwnerIdanduserIdandcancellationstatus,
    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":branchIdandType,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":detailsbasedontype,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=True, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":detailsbasedonfloorIdandtypeandfromdateandtodate,
    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":branchIdandtypeandfromdateandtodate,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=True, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":blockIdandtypeandfromdateandtodate,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=True, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":parkingOwnerIdandtypeandfromdateandtodate,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":typeandfromdateandtodate,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=True, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsbasedonbookingIdorpinnoorvehiclenumber,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=True, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=True, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":detailsbasedontypeandfloorandvehiclenumberorbookingId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=True, toTime=True, number=False, slotId=False, phoneNumber=False, category=False":getBookingDetailsBasedOnDateTime,
    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=True, toTime=True, number=False, slotId=False, phoneNumber=False, category=True":getBookingDetailsBasedOnDateTimeCategory,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=True, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=True, slotId=False, phoneNumber=False, category=False":DetailsBasedOnfloorIdandTypeandNumber,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=True, phoneNumber=False, category=False":getbookingDetailsBasedOnslotId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=True, category=False":getbookingDetailsBasedOnPhoneNumber,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=True, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":detailsBasedOnTypeandInOutDetails,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=True, blockId=False, parkingOwnerId=False, bookingId=True, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getextendedAmountAndTax,
    "branchId=False, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnPaymentTypeAndTypeRE,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnBookingAndTypeRE,
    "branchId=False, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnBookingPaymentTypeAndTypeRE,
    "branchId=False, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnBookingPaymentUserIdTypeAndTypeRE,
    "branchId=False, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=True":getDetailsBasedOnBookingPaymentCategoryTypeAndTypeRE,
    "branchId=False, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=True":getDetailsBasedOnBookingPaymentCategoryUserIdAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnBranchIdPaymentTypeAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnBranchIdBookingAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnBranchIdBookingPaymentTypeAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnBranchIdBookingPaymentTypeUserIdAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=True":getDetailsBasedOnBranchIdBookingcategoryAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=True":getDetailsBasedOnBranchIdBookingPaymentTypecategoryAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=True, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=True":getDetailsBasedOnBranchIdBookingPaymentTypecategoryUserIdAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnBranchIdPaymentTypUserIdAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=True":getDetailsBasedOnBranchIdPaymentTypecategoryAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=True, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=True":getDetailsBasedOnBranchIdPaymentTypecategoryUserIdAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=True":getDetailsBasedOnBranchIdcategoryAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getDetailsBasedOnBranchIdUserIdAndTypeRE,
    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=True, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=True, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=True":getDetailsBasedOnBranchIdUserIdCategoryAndTypeRE,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetails,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=True, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=True, toTime=True, number=False, slotId=False, phoneNumber=False, category=False":getbookingSlotsBasedOnFromTimeToTimeFromDate,
    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=True, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=True, toTime=True, number=False, slotId=False, phoneNumber=False, category=False":getbookingSlotsBasedOnFromTimeToTimeFromDateBranchId,
    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=True, toTime=True, number=False, slotId=False, phoneNumber=False, category=False":getbookingSlotsBasedOnFromTimeToTimeFromDateToDateBranchId,
    "branchId=True, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=True, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingSlotsBasedOnFromDateToDateBranchId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=True, toTime=True, number=False, slotId=False, phoneNumber=False, category=False":getbookingSlotsBasedOnFromTimeToTimeToDate,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=True, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingSlotsBasedOnFromDate,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingSlotsBasedOnToDate,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=True, Type=False, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=True, phoneNumber=False, category=False":getbookingDetailsBasedOnbookingIdSlotId,
    "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=True, Type=True, fromDate=False, toDate=False, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False, slotId=False, phoneNumber=False, category=False":getbookingDetailsBasedOnbookingIdType    
    # "branchId=False, paymentStatus=False, paymentType=False, cancellationStatus=False, bookingType=False, bookingDurationType=False, booking=False, userId=False, floorId=False, blockId=False, parkingOwnerId=False, bookingId=False, Type=False, fromDate=False, toDate=True, loginType=False, createdBy=False, createdDate=False, inOutDetails=False, subscriptionId=False, fromTime=False, toTime=False, number=False":getbookingSlotsBasedOnToDate
   
}



##################################################################################################################
@router.get('')
async def bookingGet(branchId:Optional[int]=Query(None),paymentStatus:Optional[str]=Query(None),paymentType:Optional[str]=Query(None),cancellationStatus:Optional[str]=Query(None),bookingType:Optional[str]=Query(None),bookingDurationType:Optional[str]=Query(None),booking:Optional[str]=Query(None),userId:Optional[int]=Query(None),floorId:Optional[int]=Query(None),blockId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None),bookingId:Optional[int]=Query(None),Type:Optional[str]=Query(None),fromDate:Optional[datetime]=Query(None),toDate:Optional[datetime]=Query(None),loginType:Optional[str]=Query(None),createdBy:Optional[int]=Query(None),createdDate:Optional[datetime]=Query(None),inOutDetails:Optional[str]=Query(None), subscriptionId:Optional[int]=Query(None), fromTime:Optional[time]=Query(None), toTime:Optional[time]=Query(None), number:Optional[int]=Query(None), slotId:Optional[int]=Query(None), phoneNumber:Optional[str]=Query(None), category:Optional[int]=Query(None), db:Cursor = Depends(get_cursor)):
    try:
        st = f"branchId={True if branchId else False}, paymentStatus={True if paymentStatus else False}, paymentType={True if paymentType else False}, cancellationStatus={True if cancellationStatus else False}, bookingType={True if bookingType else False}, bookingDurationType={True if bookingDurationType else False}, booking={True if booking else False}, userId={True if userId else False}, floorId={True if floorId else False}, blockId={True if blockId else False}, parkingOwnerId={True if parkingOwnerId else False}, bookingId={True if bookingId else False}, Type={True if Type else False}, fromDate={True if fromDate else False}, toDate={True if toDate else False}, loginType={True if loginType else False}, createdBy={True if createdBy else False}, createdDate={True if createdDate else False}, inOutDetails={True if inOutDetails else False}, subscriptionId={True if subscriptionId else False}, fromTime={True if fromTime else False}, toTime={True if toTime else False}, number={True if number!=None else False}, slotId={True if slotId else False}, phoneNumber={True if phoneNumber else False}, category={True if category else False}"
        return await bookingDict[st](branchId,paymentStatus,paymentType,cancellationStatus,bookingType,bookingDurationType,booking,userId,floorId,blockId,parkingOwnerId,bookingId,Type,fromDate,toDate,loginType,createdBy,createdDate,inOutDetails,subscriptionId,fromTime,toTime,number,slotId,phoneNumber,category, db)

    except Exception as e:
        print("Exception as bookingGet ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


@router.post('')
async def postBookingMaster(request:schemas.BookingMaster,background_tasks: BackgroundTasks,db: Cursor = Depends(get_cursor)):
    try:
        if request.userSlotDetails != None:
            userSlotDetails = Parallel(
                n_jobs=-1, verbose=True)(delayed(VehicleMasterCallFunction)(i) for i in request.userSlotDetails)
            userSlotDetails = json.dumps(userSlotDetails)
        else:
            userSlotDetails = None
        if request.extraFeesDetails != None:
            extraFeesDetail = Parallel(
                n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.extraFeesDetails)
            extraFeesDetails = json.dumps(extraFeesDetail)
        else:
            extraFeesDetails = None
        if request.vehicleHeaderDetails != None:
            vehicleHeaderDetail = Parallel(
                n_jobs=-1, verbose=True)(delayed(VehicleMasterCallFunction)(i) for i in request.vehicleHeaderDetails)
            vehicleHeaderDetailsData = json.dumps(vehicleHeaderDetail,indent=4, sort_keys=True, default=str)
        else:
            vehicleHeaderDetail = None
        if request.extraFeaturesDetails != None:
            extraFeaturesDetail = Parallel(
                n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.extraFeaturesDetails)
            extraFeaturesDetails = json.dumps(extraFeaturesDetail)
        else:
            extraFeaturesDetails = None
    

        data1=[]
        for i in extraFeaturesDetail:
            data1.append({'floorFeaturesId':i['floorFeaturesId'],'count':i['count']})
        taxAmount=await getTaxOnfloorfeaturesIds(data1)
        tax=taxAmount[0]['extraFeaturesTaxAmount']
        tax1=taxAmount[0]['extraFeaturesTotalAmount']
        
        
        data2=[]
        for n in extraFeesDetail:
            data2.append({'priceId':n['priceId'],'count':n['count']})
        pricetaxAmount=await getTaxOnpriceId(data2)
        taxAmt=pricetaxAmount[0]['extraFeesTaxAmount']
        taxAmt1=pricetaxAmount[0]['extraFeesTotalAmount']


        data=request.taxId
        val=await getPassTransactionTaxId(data)
        taxPercentage=((request.totalAmount-((tax1+taxAmt1)*(val['taxPercentage'] / 100)+(tax+taxAmt))))
            

        parkingName = redis_client.hget('parkingOwnerMaster', request.parkingOwnerId)
        branchName = redis_client.hget('branchMaster', request.branchId)
        blockName = redis_client.hget('blockMaster', request.blockId)
        floorName = redis_client.hget('floorMaster', request.floorId)
        userName = redis_client.hget('userMaster', request.userId)
        emailId = redis_client.hget('userMaster', request.userId)
        paymentTypeName = redis_client.hget('configMaster', request.paymentType)

        parkingName=parkingName.decode("utf-8") if parkingName else None
        branchName=branchName.decode("utf-8") if branchName else None
        blockName=blockName.decode("utf-8") if blockName else None
        floorName=floorName.decode("utf-8") if floorName else None
        userName=userName.decode("utf-8") if userName else None
        emailId=emailId.decode("utf-8") if emailId else None
        paymentTypeName=paymentTypeName.decode("utf-8") if paymentTypeName else None

        await db.execute(f"""EXEC [dbo].[postBookingMaster]
                                        @parkingOwnerId =?,
                                        @parkingName=?,
        								@branchId =?,
                                        @branchName=?,
        								@blockId =?,
                                        @blockName=?,
        								@floorId =?,
                                        @floorName=?,
        								@userId =?,
                                        @userName=?,
                                        @phoneNumber =?,
                                        @emailId=?,
        								@booking =?,
        								@loginType =?,
        								@bookingDurationType =?,
        								@fromTime =?,
        								@toTime =?,
        								@fromDate =?,
        								@toDate =?,
        								@accessories =?,
        								@bookingType =?,
        								@subscriptionId =?,
                                        @taxId=?,
        								@totalAmount=?,
        								@paidAmount =?,
        								@paymentStatus =?,
        								@paymentType =?,
                                        @paymentTypeName=?,
        								@offerId =?,
        								@transactionId=?,
                                        @bankName=?,
                                        @bankReferenceNumber=?,
                                        @pinNo=?,
        								@createdBy =?,
                                        @taxpercentage=?,
        								@vehicleHeaderJson =?,
        								@extraFeaturesJson =?,
        								@userSlotJson=?,
        								@extraFeesJson=?
        								""",(
                                         request.parkingOwnerId,
                                         parkingName,
                                         request.branchId,
                                         branchName,
                                         request.blockId,
                                         blockName,
                                         request.floorId,
                                         floorName,
                                         request.userId,
                                         userName,
                                         request.phoneNumber,
                                         emailId,
                                         request.booking,
                                         request.loginType,
                                         request.bookingDurationType,
                                         request.fromTime,
                                         request.toTime,
                                         request.fromDate,
                                         request.toDate,
                                         request.accessories,
                                         request.bookingType,
                                         request.subscriptionId,
                                         request.taxId,
                                         request.totalAmount,
                                         request.paidAmount,
                                         request.paymentStatus,
                                         request.paymentType,
                                         paymentTypeName,
                                         request.offerId,
                                         request.transactionId,
                                         request.bankName,
                                         request.bankReferenceNumber,
                                         request.pinNo,
                                         request.createdBy,
                                         taxPercentage,
                                         vehicleHeaderDetailsData,
                                         extraFeaturesDetails,
                                         userSlotDetails,
                                         extraFeesDetails
                                     ))
        rows = await db.fetchall()
        if rows[0][1]==1:
            for k in vehicleHeaderDetail:
                await publish(queueName='slotManagement', message ={
                            'action':'postbooking',
                            'body':{
                                'slotId':k['slotId']
                            }
                            })
            bookingmail.delay(request.userId)
            return{
                "statusCode":int(rows[0][1]),
                "response":rows[0][0]
            }
        else:
            return{            
                'response': 'data not Added',
                'statusCode':0
                }
    except Exception as e:
        print("Exception as postBookingMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

@router.put('')
async def putPaymentStatus(request:schemas.PutPaymentStatus,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putPaymentStatus] 
                                        @paymentStatus=?,
                                        @bookingId=?,
                                        @transactionId=?,
                                        @bankName=?,
                                        @bankReferenceNumber=?""", 
                                    (request.paymentStatus,
                                    request.bookingId, 
                                    request.transactionId, 
                                    request.bankName, 
                                    request.bankReferenceNumber))
        rows=await db.fetchall()
        await db.commit()
        if int(rows[0][1]) == 1 and rows[0][2] == 'P':
            putPaymentStatusmail.delay(json.loads(rows[0][3]))
            return{
                "statusCode":int(rows[0][1]),
                "response":rows[0][0]
            }
    except Exception as e:
        print("Exception as putPaymentStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

@routerDateTimeExtend.put('')
async def putBookingDateTimeExtend(request:schemas.PutBookingDateTimeExtend,db:Cursor=Depends(get_cursor)):
    try:
        paymentTypeName = redis_client.hget('configMaster', request.paymentType)
        paymentTypeName=paymentTypeName.decode("utf-8") if paymentTypeName else None

        await db.execute(f"""EXEC [dbo].[putBookingDateTime]
                                        @bookingDurationType =?,
                                                @toTime=?,
                                                @toDate =?,
                                                @taxAmount=?,
                                                @paidAmount=?,
												@totalAmount=?,
                                                @bookingId =?,
                                                @vehicleHeaderId=?,
                                                @updatedBy=?,
                                                @vehicleStatus=?,
                                                @slotId=?,
                                                @paymentType=?,
                                                @paymentTypeName=?,
                                                @transactionId =?,
                                                @bankName =?,
                                                @bankReferenceNumber =?
                                                """,
                                    (
                                     request.bookingDurationType,
                                     request.toTime,
                                     request.toDate,
                                     request.taxAmount,
                                     request.paidAmount,
                                     request.totalAmount,
                                     request.bookingId,
                                     request.vehicleHeaderId,
                                     request.updatedBy,
                                     request.vehicleStatus,
                                     request.slotId,
                                     request.paymentType,
                                     paymentTypeName,
                                     request.transactionId,
                                     request.bankName,
                                     request.bankReferenceNumber

                                    )
                                    )
        rows=await db.fetchall()
        await db.commit()
        if int(rows[0][1]) == 1 and rows[0][2] == 'P':        
            await publish(queueName='slotManagement', message ={
                        'action':'datetimeextend',
                        'body':{
                            'slotId': request.slotId
                        }
                        })
            bookingdatetimeExtendmail.delay(json.loads(rows[0][3]))
            return{
                "statusCode":int(rows[0][1]),
                "response":rows[0][0]
            }
        else:
            return{            
                "statusCode":int(rows[0][1]),
                "response":rows[0][0]
                }
    except Exception as e:
        print("Exception as putBookingDateTimeExtend ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

@routerpaidAmount.put('')
async def putBookingPaidAmount(request:schemas.PutBookingPaidAmount,db:Cursor=Depends(get_cursor)):
    try:
        paymentTypeName = redis_client.hget('configMaster', request.paymentType)
        paymentTypeName=paymentTypeName.decode("utf-8") if paymentTypeName else None

        await db.execute(f"""EXEC [dbo].[putBookingPaidAmount]
                                                    @paidAmount=?,
                                                    @bookingId =?,
                                                    @paymentStatus=?,
                                                    @transactionId =?,
                                                    @bankName =?,
                                                    @bankReferenceNumber=?,
                                                    @paymentType =?,
                                                    @paymentTypeName=?,
                                                    @updatedBy =?
                                                """,
                                    (
                                        request.paidAmount,
                                        request.bookingId,
                                        request.paymentStatus,
                                        request.transactionId,
                                        request.bankName,
                                        request.bankReferenceNumber,
                                        request.paymentType,
                                        paymentTypeName,
                                        request.updatedBy

                                    )
                                    )
        rows=await db.fetchall()
        await db.commit()
        if int(rows[0][1]) == 1 and rows[0][2] == 'P':
            putbookingpaidAmountdmail.delay(json.loads(rows[0][3]))
            return{
                "statusCode":int(rows[0][1]),
                "response":rows[0][0]
            }
        else:
            return{            
                'response': 'data not updated',
                'statusCode':0
                }
    except Exception as e:
        print("Exception as putBookingPaidAmount",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }



