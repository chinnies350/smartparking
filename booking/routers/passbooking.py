from datetime import date, datetime
from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from fastapi import Response
from aioodbc.cursor import Cursor
from eventsServer import publish
import schemas
import routers
from typing import Optional
from fastapi import Query
# from routers.config import engine 
from routers.config import get_cursor,redis_client
# from task import passlot
import time
import json,os 
import asyncio
from joblib import Parallel, delayed
from dotenv import load_dotenv
load_dotenv()


router = APIRouter(prefix="/passbooking",tags=['passbooking'])

def callFunction(i):
    return i.dict()

def VehicleMasterCallFunction(i):
    i=i.dict()
    vehicleDetails=redis_client.hget('vehicleConfigMaster', i['vehicleType'])
    i['vehicleTypeName'],i['vehicleImageUrl']=tuple(json.loads(vehicleDetails.decode("utf-8")).values()) if vehicleDetails else None
    return i

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
        print(f'Exception as getvehicleconfigmaster {str(e)}')
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
        else:
            return {
                 'featureName':"",
                 'tax':"",
                 'totalAmount':""
            }

    except Exception as e:
        print(f'Exception as getfloorfeaturesOnextraFeatureId {str(e)}')
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
        print(f'Exception as getTaxOnfloorfeaturesId {str(e)}')
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
        print(f'Exception as getTaxOnpriceId {str(e)}')
        return {}

async def getExtraFeesFeaturesDetails(passBookingTransactionId,dic,totalAmount,db):
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
                dic['extraFeesTotalAmount']=response['response'][0]['extraFeesAmount']
        await db.execute(f"""SELECT CAST((SELECT ef.*
                                                FROM extraFeatures as ef
                                                WHERE ef.bookingPassId = ? AND ef.bookingIdType = 'P'
                                                  FOR JSON PATH) AS  varchar(max))""",(passBookingTransactionId))
        
        row = await db.fetchone()
        extraFeaturesRes=[]
        if row[0] != None:
            for i in json.loads(row[0]):
                extraFeaturesRes.append({'extraFeatureId':i['extraFeatureId'],'bookingIdType':i['bookingIdType'],'bookingPassId':i['bookingPassId'],'floorFeaturesId':i['floorFeaturesId'],'count':i['count'],'extraDetail':i.get('extraDetail'),'createdDate':i['createdDate'],'updatedDate':i.get('updatedDate')})

            dic['extraFeaturesDetail']=extraFeaturesRes
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

async def getfloorDetailsOnfloorId(floorId):
    try:
        url = f"{os.getenv('SLOT_SERVICE_URL')}/floorMaster?floorId={floorId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:              
                return {
                        'branchId':i['branchId'],
                        'branchName':i['branchName'],
                        'parkingOwnerId':i['parkingOwnerId'],
                        'parkingName':i['parkingName']
                       
                }
        else:
            return {
                 'branchId':"",
                 'branchName':"",
                 'parkingOwnerId':"",
                 'parkingName':""
               
            }
    except Exception as e:
        print(f'Exception as getfloorDetailsOnfloorId {str(e)}')
        return {}


async def modifiedvehicleconfigdetails(vehicleDetails,dic):
    data = []
    for i in vehicleDetails:

        i.update(await getvehicleconfigmaster(i["vehicleType"]))
        data.append(i)
    dic['vehicleDetails'] = data
    # dic.update(res)

async def modifiedfloorfeatures(extraFeaturesDetails,dic):
    data = []
    for i in extraFeaturesDetails:
        i.update(await getfloorfeaturesOnextraFeatureId(i["floorFeaturesId"]))
        data.append(i)
    dic['extraFeaturesDetails']= data
        # dic.update(res)

async def modifieduserslotdetails(userSlotDetails,dic):
    data = []
    for i in userSlotDetails:

        i.update(await getvehicleconfigmaster(i["vehicleType"]))
        data.append(i)
    dic['userSlotDetails'] = data

async def modifiedvehicleTypeName(vehicleOutTimeDetails,dic):
    data = []
    for i in vehicleOutTimeDetails:

        i.update(await getvehicleconfigmaster(i["vehicleType"]))
        data.append(i)
    dic['vehicleOutTimeDetails'] = data
    # dic.update(res)

async def modifiedIntimevehicleTypeName(vehicleInTimeDetails,dic):
    data = []
    for i in vehicleInTimeDetails:

        i.update(await getvehicleconfigmaster(i["vehicleType"]))
        data.append(i)
    dic['vehicleInTimeDetails'] = data

async def modifiedfloorDetails(floorId,dic):
    res  = await getfloorDetailsOnfloorId(floorId)
    dic.update (res)




async def passVehicleHeaderDetailsBasedBranchId(branchId,passId,parkingOwnerId,Type,inOutDetails,floorId,number,fromDate,toDate,db):
    try:
        if Type =='O':
            url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?branchId={branchId}"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                for i in response['response']:
                    await db.execute(f"""SELECT CAST((SELECT DISTINCT vh.* 
                                                        FROM vehicleHeader as vh
                                                        INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                        WHERE vh.bookingPassId=pbt.passTransactionId AND vh.vehicleStatus='I' AND vh.bookingIdType='P' AND pbt.passTransactionId=?
                                                    FOR JSON PATH) AS VARCHAR(MAX))""",(i['parkingPassTransId']))

                    row = await db.fetchone()
                    data=[]
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
            return{
                "response":"Data Not Found",
                "statusCode":0
            }
        elif Type =='I':
            url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?branchId={branchId}"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                for i in response['response']:
                    await db.execute(f"""SELECT CAST((SELECT DISTINCT vh.* 
                                                        FROM vehicleHeader as vh
                                                        INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                        WHERE vh.bookingPassId=pbt.passTransactionId AND vh.vehicleStatus IS NULL AND vh.bookingIdType='P' AND pbt.passTransactionId=?
                                                    FOR JSON PATH) AS VARCHAR(MAX))""",(i['parkingPassTransId']))

                    row = await db.fetchone()
                    data=[]
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
            return{
                "response":"Data Not Found",
                "statusCode":0
            }                                
    except Exception as e:
        print("Exception as passVehicleHeaderDetailsBasedBranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def passVehicleHeaderDetailsBasedBranchIdPassId(branchId,passId,parkingOwnerId,Type,inOutDetails,floorId,number,fromDate,toDate,db):
    try:
        if Type =='O':
            url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?branchId={branchId}&passId={passId}"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                for i in response['response']:
                    await db.execute(f"""SELECT CAST((SELECT DISTINCT vh.* 
                                                        FROM vehicleHeader as vh
                                                        INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                        WHERE vh.bookingPassId=pbt.passTransactionId AND vh.vehicleStatus='I' AND vh.bookingIdType='P' AND pbt.passTransactionId=?
                                                    FOR JSON PATH) AS VARCHAR(MAX))""",(i['parkingPassTransId']))

                    row = await db.fetchone()
                    data=[]
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
            return{
                "response":"Data Not Found",
                "statusCode":0
            }
        elif Type =='I':
            url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?branchId={branchId}&passId={passId}"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                for i in response['response']:
                    await db.execute(f"""SELECT CAST((SELECT DISTINCT vh.* 
                                                        FROM vehicleHeader as vh
                                                        INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                        WHERE vh.bookingPassId=pbt.passTransactionId AND vh.vehicleStatus IS NULL AND vh.bookingIdType='P' AND pbt.passTransactionId=?
                                                    FOR JSON PATH) AS VARCHAR(MAX))""",(i['parkingPassTransId']))

                    row = await db.fetchone()
                    data=[]
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
            return{
                "response":"Data Not Found",
                "statusCode":0
            }                                
    except Exception as e:
        print("Exception as passVehicleHeaderDetailsBasedBranchIdPassId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def passVehicleHeaderDetailsBasedparkingOwnerId(branchId,passId,parkingOwnerId,Type,inOutDetails,floorId,number,fromDate,toDate,db):
    try:
        if Type =='O':
            url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?parkingOwnerId={parkingOwnerId}"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                for i in response['response']:
                    await db.execute(f"""SELECT CAST((SELECT DISTINCT vh.* 
                                                        FROM vehicleHeader as vh
                                                        INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                        WHERE vh.bookingPassId=pbt.passTransactionId AND vh.vehicleStatus='I' AND vh.bookingIdType='P' AND pbt.passTransactionId=?
                                                    FOR JSON PATH) AS VARCHAR(MAX))""",(i['parkingPassTransId']))

                    row = await db.fetchone()
                    data=[]
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
            return{
                "response":"Data Not Found",
                "statusCode":0
            }
        elif Type =='I':
            url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?parkingOwnerId={parkingOwnerId}"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                for i in response['response']:
                    await db.execute(f"""SELECT CAST((SELECT DISTINCT vh.* 
                                                        FROM vehicleHeader as vh
                                                        INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                        WHERE vh.bookingPassId=pbt.passTransactionId AND vh.vehicleStatus IS NULL AND vh.bookingIdType='P' AND pbt.passTransactionId=?
                                                    FOR JSON PATH) AS VARCHAR(MAX))""",(i['parkingPassTransId']))

                    row = await db.fetchone()
                    data=[]
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
            return{
                "response":"Data Not Found",
                "statusCode":0
            }                                
    except Exception as e:
        print("Exception as passVehicleHeaderDetailsBasedparkingOwnerId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def passVehicleHeaderDetailsBasedBranchIdInOutDetails(branchId,passId,parkingOwnerId,Type,inOutDetails,floorId,number,fromDate,toDate,db):
    try:
        if Type =='O':
            url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?branchId={branchId}"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                for i in response['response']:
                    await db.execute(f"""DECLARE @tempVar VARCHAR(10);
                                    BEGIN TRY
                                        SET @tempVar=CAST(? AS int)
                                    END TRY
                                    BEGIN CATCH
                                        SET @tempVar=-1
                                    END CATCH
                                    SELECT CAST((SELECT DISTINCT vh.* 
                                                        FROM vehicleHeader as vh
                                                        INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                        WHERE vh.bookingPassId=pbt.passTransactionId AND vh.vehicleStatus='I' AND vh.bookingIdType='P' AND pbt.passTransactionId=? AND ({i['passId']}=@tempVar  OR vh.vehicleNumber=?)
                                                    FOR JSON PATH) AS VARCHAR(MAX))""",(inOutDetails,i['parkingPassTransId'],inOutDetails))

                    row = await db.fetchone()
                    data=[]
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
            return{
                "response":"Data Not Found",
                "statusCode":0
            }
        elif Type =='I':
            url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?branchId={branchId}"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                for i in response['response']:
                    await db.execute(f"""DECLARE @tempVar VARCHAR(10);
                                    BEGIN TRY
                                        SET @tempVar=CAST(? AS int)
                                    END TRY
                                    BEGIN CATCH
                                        SET @tempVar=-1
                                    END CATCH
                                    SELECT CAST((SELECT DISTINCT vh.* 
                                                        FROM vehicleHeader as vh
                                                        INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                        WHERE vh.bookingPassId=pbt.passTransactionId AND vh.vehicleStatus IS NULL AND vh.bookingIdType='P' AND pbt.passTransactionId=? AND ({i['passId']}=@tempVar  OR vh.vehicleNumber=?)
                                                    FOR JSON PATH) AS VARCHAR(MAX))""",(inOutDetails,i['parkingPassTransId'],inOutDetails))

                    row = await db.fetchone()
                    data=[]
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
            return{
                "response":"Data Not Found",
                "statusCode":0
            }                                
    except Exception as e:
        print("Exception as passVehicleHeaderDetailsBasedBranchIdInOutDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def passVehicleHeaderDetailsBasedFloorId(branchId,passId,parkingOwnerId,Type,inOutDetails,floorId,number,fromDate,toDate,db):
    try:
        data=[]
        if Type =='O':
            url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                for i in response['response']: 
                    await db.execute(f"""SELECT CAST((SELECT DISTINCT vh.* 
                                                        FROM vehicleHeader as vh
                                                        INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                        WHERE vh.bookingPassId=pbt.passTransactionId AND vh.vehicleStatus='I' AND vh.bookingIdType='P' AND pbt.floorId=? AND pbt.passTransactionId=?
                                                        ORDER BY vh.vehicleHeaderId
                                                        OFFSET 10 * ? ROWS
                                                        FETCH NEXT 10 ROWS ONLY 
                                                    FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,i['parkingPassTransId'],number))

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
        elif Type =='I':
            data=[]
            url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                for i in response['response']: 
                    await db.execute(f"""SELECT CAST((SELECT DISTINCT vh.* 
                                                        FROM vehicleHeader as vh
                                                        INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                        WHERE vh.bookingPassId=pbt.passTransactionId AND vh.vehicleStatus IS NULL AND vh.bookingIdType='P' AND pbt.floorId=? AND pbt.passTransactionId=?
                                                        ORDER BY vh.vehicleHeaderId
                                                        OFFSET 10 * ? ROWS
                                                        FETCH NEXT 10 ROWS ONLY
                                                    FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,i['parkingPassTransId'],number))

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
        print("Exception as passVehicleHeaderDetailsBasedFloorId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def passDetailsBasedInOutDetails(branchId,passId,parkingOwnerId,Type,inOutDetails,floorId,number,fromDate,toDate,db):
    try:
        data=[]
        url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']: 
                await db.execute(f"""DECLARE @tempVar VARCHAR(10);
                                        BEGIN TRY
                                            SET @tempVar=CAST(? AS int)
                                        END TRY
                                        BEGIN CATCH
                                            SET @tempVar=-1
                                        END CATCH
                                        SELECT CAST((SELECT DISTINCT pbt.*,ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=pbt.passBookingTransactionId AND vh.bookingIdType='P' FOR JSON PATH),'[]')AS vehicleDetails,
                                        ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=pbt.passBookingTransactionId AND vh.vehicleStatus='I' AND vh.bookingIdType='P' FOR JSON PATH),'[]')AS vehicleOutTimeDetails,
                                        ISNULL((SELECT vh.* FROM vehicleHeader AS vh WHERE vh.bookingPassId=pbt.passBookingTransactionId AND vh.inTime IS NULL AND vh.bookingIdType='P' FOR JSON PATH),'[]')AS vehicleInTimeDetails,
                                        ISNULL((SELECT ef.* FROM extraFeatures AS ef WHERE ef.bookingPassId=pbt.passBookingTransactionId AND ef.bookingIdType='P' FOR JSON PATH),'[]') AS extraFeaturesDetails,
                                        ISNULL((SELECT exf.* FROM extraFees AS exf WHERE exf.bookingPassId=pbt.passBookingTransactionId AND exf.bookingIdType='P' FOR JSON PATH),'[]')AS extraFeesDetails,
                                        ISNULL((SELECT uss.* FROM userSLot AS uss WHERE uss.bookingPassId=pbt.passBookingTransactionId AND uss.bookingIdType='P' FOR JSON PATH),'[]')AS userSlotDetails
                                        FROM passBookingTransaction AS pbt
                                        INNER JOIN vehicleHeader AS vh
                                        ON vh.bookingPassId=pbt.passBookingTransactionId AND vh.bookingIdType='P'
                                        WHERE (pbt.passBookingTransactionId=@tempVar OR vh.vehicleNumber=?) AND pbt.passTransactionId=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(inOutDetails,inOutDetails,i['parkingPassTransId']))

                row = await db.fetchone()
                if row[0] != None:
                    data=json.loads(row[0])
                    for dic in data:
                        await asyncio.gather(
                                            modifiedvehicleconfigdetails(dic['vehicleDetails'],dic),
                                            modifiedvehicleTypeName(dic['vehicleOutTimeDetails'],dic),
                                            modifiedIntimevehicleTypeName(dic['vehicleInTimeDetails'],dic),
                                            modifiedfloorfeatures(dic['extraFeaturesDetails'],dic),
                                            modifieduserslotdetails(dic['userSlotDetails'],dic),
                                            getExtraFeesFeaturesDetails(dic['passBookingTransactionId'],dic,dic.get('totalAmount'),db),
                                            modifiedfloorDetails(dic['floorId'],dic)                                           
                                            )
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
        print("Exception as passDetailsBasedInOutDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def passVehicleHeaderDetailsBasedBranchIdFromaAndTodate(branchId,passId,parkingOwnerId,Type,inOutDetails,floorId,number,fromDate,toDate,db):
    try:
        url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction?branchId={branchId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:
                await db.execute(f"""SELECT CAST((SELECT DISTINCT vh.* 
                                                    FROM vehicleHeader as vh
                                                    INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                    WHERE vh.bookingPassId=pbt.passTransactionId AND vh.vehicleStatus='I' AND vh.bookingIdType='P' AND pbt.passTransactionId=?
                                                    AND CAST(pbt.createdDate AS DATE) BETWEEN '{fromDate}' AND '{toDate}' AND vh.vehicleStatus !='O'
                                                FOR JSON PATH) AS VARCHAR(MAX))""",(i['parkingPassTransId']))

                row = await db.fetchone()
                data=[]
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
        return{
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as passVehicleHeaderDetailsBasedBranchIdFromaAndTodate ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def passVehicleHeaderDetails(branchId,passId,parkingOwnerId,Type,inOutDetails,floorId,number,fromDate,toDate,db):
    try:
        url=f"{os.getenv('PARKING_PASS_MODULE_URL')}/passTransaction"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:        
                await db.execute(f"""SELECT CAST((SELECT DISTINCT vh.* 
                                                        FROM vehicleHeader as vh
                                                        INNER JOIN passBookingTransaction as pbt ON pbt.passTransactionId=vh.bookingPassId 
                                                        WHERE vh.bookingPassId=pbt.passTransactionId AND vh.bookingIdType='P' AND pbt.passTransactionId=? 
                                                FOR JSON PATH) AS VARCHAR(MAX))""",(i['parkingPassTransId']))

                row = await db.fetchone()
                data=[]
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
        print("Exception as passVehicleHeaderDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


    

PassDict = {
   "branchId=True,passId=False,parkingOwnerId=False,Type=True,inOutDetails=False,floorId=False,number=False,fromDate=False,toDate=False":passVehicleHeaderDetailsBasedBranchId,
   "branchId=True,passId=True,parkingOwnerId=False,Type=True,inOutDetails=False,floorId=False,number=False,fromDate=False,toDate=False":passVehicleHeaderDetailsBasedBranchIdPassId,
   "branchId=False,passId=False,parkingOwnerId=True,Type=True,inOutDetails=False,floorId=False,number=False,fromDate=False,toDate=False":passVehicleHeaderDetailsBasedparkingOwnerId,
   "branchId=True,passId=False,parkingOwnerId=False,Type=True,inOutDetails=True,floorId=False,number=False,fromDate=False,toDate=False":passVehicleHeaderDetailsBasedBranchIdInOutDetails,
   "branchId=False,passId=False,parkingOwnerId=False,Type=True,inOutDetails=False,floorId=True,number=True,fromDate=False,toDate=False":passVehicleHeaderDetailsBasedFloorId,
   "branchId=False,passId=False,parkingOwnerId=False,Type=False,inOutDetails=True,floorId=False,number=False,fromDate=False,toDate=False":passDetailsBasedInOutDetails,
   "branchId=True,passId=False,parkingOwnerId=False,Type=False,inOutDetails=False,floorId=False,number=False,fromDate=True,toDate=True":passVehicleHeaderDetailsBasedBranchIdFromaAndTodate,
   "branchId=False,passId=False,parkingOwnerId=False,Type=False,inOutDetails=False,floorId=False,number=False,fromDate=False,toDate=False":passVehicleHeaderDetails

}

##################################################################################################################
@router.get('')
async def bookingPassGet(branchId:Optional[int]=Query(None),passId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None),Type:Optional[str]=Query(None),inOutDetails:Optional[str]=Query(None),floorId:Optional[int]=Query(None),number:Optional[int]=Query(None),fromDate:Optional[datetime]=Query(None),toDate:Optional[datetime]=Query(None),db:Cursor = Depends(get_cursor)):
    st = f"branchId={True if branchId else False},passId={True if passId else False},parkingOwnerId={True if parkingOwnerId else False},Type={True if Type else False},inOutDetails={True if inOutDetails else False},floorId={True if floorId else False},number={True if number!=None else False},fromDate={True if fromDate else False},toDate={True if toDate else False}"
    return await PassDict[st](branchId,passId,parkingOwnerId,Type,inOutDetails,floorId,number,fromDate,toDate,db)



@router.post('')
async def postPassBooking(request:schemas.PassBokking,db: Cursor = Depends(get_cursor)):
    try:

        if request.userSlotDetails!=None:
            userSlotDetail = Parallel(n_jobs=-1, verbose=True)(delayed(VehicleMasterCallFunction)(i) for i in request.userSlotDetails)
            userSlotDetailData=json.dumps(userSlotDetail)
        else:
            userSlotDetail=None
        if request.extraFeesDetails!=None:
            extraFeesDetail = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.extraFeesDetails)
            extraFeesDetails=json.dumps(extraFeesDetail)
        else:
            extraFeesDetails=None 
        if request.vehicleHeaderDetails!=None:
            vehicleHeaderDetails = Parallel(n_jobs=-1, verbose=True)(delayed(VehicleMasterCallFunction)(i) for i in request.vehicleHeaderDetails)
            vehicleHeaderDetails=json.dumps(vehicleHeaderDetails)
        else:
            vehicleHeaderDetails=None
        if request.extraFeaturesDetails!=None:
            extraFeaturesDetail = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.extraFeaturesDetails)
            extraFeaturesDetails=json.dumps(extraFeaturesDetail)
        else:
            extraFeaturesDetails=None

        data=[]
        for i in extraFeaturesDetail:
            data.append({'floorFeaturesId':i['floorFeaturesId'],'count':i['count']})
        taxAmount=await getTaxOnfloorfeaturesIds(data)
        tax=taxAmount[0]['extraFeaturesTaxAmount']
        
        data1=[]
        for n in extraFeesDetail:
            data1.append({'priceId':n['priceId'],'count':n['count']})
        pricetaxAmount=await getTaxOnpriceId(data1)
        taxAmt=pricetaxAmount[0]['extraFeesTaxAmount']

        
        blockName = redis_client.hget('blockMaster', request.blockId)
        floorName = redis_client.hget('floorMaster', request.floorId)
        paymentTypeName = redis_client.hget('configMaster', request.paymentType)

        
        blockName=blockName.decode("utf-8") if blockName else None
        floorName=floorName.decode("utf-8") if floorName else None
        paymentTypeName=paymentTypeName.decode("utf-8") if paymentTypeName else None
        
        await db.execute(f""" EXEC [dbo].[postPassBooking]
                                    @passTransactionId =?,
                                    @blockId =?,
                                    @blockName=?,
                                    @floorId =?,
                                    @floorName=?,
                                    @totalAmount=?,
                                    @paymentStatus=?,
                                    @paymentType=?,
                                    @paymentTypeName=?,
                                    @transactionId=?,
                                    @bankName=?,
                                    @bankReferenceNumber=?,
                                    @createdBy=?,
                                    @tax =?,
                                    @taxAmt=?,
                                    @vehicleHeaderJson=?,
                                    @extraFeaturesJson=?,
                                    @userSlotJson=?,
                                    @extraFeesJson=?
                                    """,
                                    (
                                    request.passTransactionId,
                                    request.blockId,
                                    blockName,
                                    request.floorId,
                                    floorName,
                                    request.totalAmount,
                                    request.paymentStatus,
                                    request.paymentType,
                                    paymentTypeName,
                                    request.transactionId,
                                    request.bankName,
                                    request.bankReferenceNumber,
                                    request.createdBy,
                                    tax,
                                    taxAmt,
                                    vehicleHeaderDetails,
                                    extraFeaturesDetails,
                                    userSlotDetailData,
                                    extraFeesDetails
                                    ))
        rows=await db.fetchall()
        if rows[0][1]==1:
            for k in userSlotDetail:
                await publish(queueName='slotManagement', message ={
                            'action':'passbooking',
                            'body':{
                                'slotId': k['slotId']
                            }
                            })
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
        print("Exception as postPassBooking ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }
