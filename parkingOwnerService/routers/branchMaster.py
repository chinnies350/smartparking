from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from fastapi import Response
from aioodbc.cursor import Cursor
from routers.eventsServer import publish
import schemas
import routers
# from routers.config import engine 
from routers.config import get_cursor
from task import passlot
from typing import Optional
from fastapi import Query
import time
import json,os
import asyncio
from joblib import Parallel, delayed 
from task import postBranchName
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/branchMaster",tags=['branchMaster'])

def callFunction(i):
    return i.dict()

async def getminpriceBasedOnbranchId(branchId):
    try:
        url=f"{os.getenv('SLOT_SERVICE_URL')}/priceMaster?branchId={branchId}&idType=V"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0]['minPrice']
        return ""
    except Exception as e:
        print("Exception as getminpriceBasedOnbranchId ",str(e))
        return ""

async def getslotsBasedOnbranchId(branchId):
    try:
        url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        url=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?branchId={branchId}&activeStatus={response['response']}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0]['totalSlot']
        return ""
    except Exception as e:
        print("Exception as getSlotDetails ",str(e))
        return ""


async def getratingsBasedOnbranchId(branchId,dic):
    try:        
        url=f"{os.getenv('USER_SERVICE_URL')}/feedBackMaster?branchId={branchId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        rating=[]
        if response['statusCode'] == 1:
            for i in response['response']:                 
                rating.append(i['feedbackRating'])
            avg = sum(rating) / len(rating)        

            dic['rating']=avg
        else:
            dic['rating']=0        
     

    except Exception as e:
        print("Exception as getratingsBasedOnbranchId",str(e))
        return ""

# async def getSlotExist(branchId):
#     try:
#         url=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?slotExist={branchId}"
#         response = await routers.client.get(url)
#         response = json.loads(response.text)
#         if response['statusCode'] == 1:
#             return response['response'][0]['slotExist']
#         return ""
#     except Exception as e:
#         print("Exception as getSlotExist ",str(e))
#         return ""

async def getVehiclename(branchId,activeStatus):
    try:
        url=f"{os.getenv('SLOT_SERVICE_URL')}/floorVehicleMaster?branchId={branchId}&activeStatus={activeStatus}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0]['vehicleName']

        return ""
                
    except Exception as e:
        print(f'Exception as getVehiclename {str(e)}')
        return ""

async def getSlotExist(branchId):
    try:
        url=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?slotExist={branchId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0]['slotExist']
        return ""
    except Exception as e:
        print("Exception as getSlotExist ",str(e))
        return ""
    
async def getBranchOptions(branchId):
    try:
        url=f"{os.getenv('ADMIN_SERVICE_URL')}/parkingOwnerConfig?branchId={branchId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0]['branchOptions']
        return ""
    except Exception as e:
        print("Exception as getBranchOptions ",str(e))
        return ""

async def getSlotDetails(branchId,checkBranchSlotIds,slotResponse):
    try:
        url=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?branchId={branchId}&activeStatus={slotResponse}&checkBranchSlotIds={checkBranchSlotIds}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response.get('statusCode') == 1:
            return response['response'][0]['parkingSlotIdCount']
        return 0
    except Exception as e:
        print("Exception as getSlotDetails ",str(e))
        return ""

async def getBranchSlotDetails(branchId,activeStatus):
    try:
        url=f"{os.getenv('SLOT_SERVICE_URL')}/floorVehicleMaster?branchId={branchId}&activeStatus={activeStatus}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        
        if response.get('statusCode') == 1:
            floorVehicleCapacity=response['response']
            url=f"{os.getenv('BOOKING_URL')}/vehicleHeader?branchId={branchId}"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response.get('statusCode') == 1:
                slotCapacity=response['response']
                return floorVehicleCapacity[0]['capacity'] - slotCapacity[0]['slotCapacity']
            
        return 0
    except Exception as e:
        print("Exception as getBranchSlotDetails ",str(e))
        return ""



async def modifiedminprice(branchId,dic):
    dic['minprice']=await getminpriceBasedOnbranchId(branchId)

async def modifiedslots(branchId,dic):   
     dic['slotAvailable']=await getslotsBasedOnbranchId(branchId)



async def modifiedSlotExist(branchId,dic):    
    dic['slotExist']=await getSlotExist(branchId)

async def modifiedVehicleName(branchId,activeStatus,dic):    
    res = await getVehiclename(branchId,activeStatus)
    dic['vehicleName']=res


async def modifiedSlotDetails(branchId,dic,checkBranchSlotIds,slotResponse,activeStatus,branchRes):
    if branchId not in branchRes:
        dic['slotAvailable']=await getSlotDetails(branchId,checkBranchSlotIds,slotResponse)
    else:
       dic['slotAvailable']=await getBranchSlotDetails(branchId,activeStatus) 

# async def modifiedratings(branchId,dic):
#     res = await getratingsBasedOnbranchId(branchId,dic)
#     dic.update(res)



# async def modifiedSlotExist(branchId,dic):
#     dic['slotExist']= await getSlotExist(branchId)

async def modifiedBranchOption(branchId,dic):
    dic['branchOptions']= await getBranchOptions(branchId)  


async def branchDetailsbasedOnparkingOwnerId(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE parkingOwnerId= ?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(parkingOwnerId))
        row = await db.fetchone()
        if row[0] != None:
            data=json.loads(row[0])                   
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic))

            return {
                "response":data,
                "statusCode":1
            }
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsbasedOnparkingOwnerId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def DetailsbasedOnparkingOwnerIdandactiveStatus(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):   
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE parkingOwnerId= ? AND activeStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(parkingOwnerId,activeStatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:

                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic))
            return {
                "response":data,
                "statusCode":1
            }
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as DetailsbasedOnparkingOwnerIdandactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def DetailsOnparkingOwnerIdandactiveStatusandapprovalStatus(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE parkingOwnerId= ? AND activeStatus=? AND approvalStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(parkingOwnerId,activeStatus,approvalStatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic))
            return {
                "response":data,
                "statusCode":1
            }
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as DetailsOnparkingOwnerIdandactiveStatusandapprovalStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchDetailsbasedOnbranchId(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE bmv.branchId= ? 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(branchId))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic))
            return {
                "response":data,
                "statusCode":1
            }
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsbasedOnbranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchDetailsbasedOnbranchIdandactiveStatus(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE branchId= ? AND activeStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(branchId,activeStatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsbasedOnbranchIdandactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def DetailsOnbranchIdandactiveStatusandapprovalStatus(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE branchId= ? AND activeStatus=? AND approvalStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(branchId,activeStatus,approvalStatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as DetailsOnbranchIdandactiveStatusandapprovalStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchDetailsbasedOnapprovalStatus(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE approvalStatus= ? 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(approvalStatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsbasedOnapprovalStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchDetailsbasedOnactiveStatus(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE activeStatus= ? 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic))

            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsbasedOnactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchDetailsBasedOnApprovalActiveStatus(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE activeStatus= ? AND approvalStatus= ?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus,approvalStatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic)
                                   )

            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsBasedOnApprovalActiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchDetailsbasedOnlatAndlng(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails
								,(SQRT(POWER(69.1 * (CAST(bmv.latitude AS DECIMAL(12,7)) - {lat}), 2) + POWER(69.1 * ({lng} - CAST(bmv.longitude AS DECIMAL(12,7))) * COS(bmv.latitude / 57.3), 2))* 1.60934) AS distance           
                                FROM  branchMasterView as bmv 
                                FOR JSON PATH) AS VARCHAR(MAX))""")
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(
                        getratingsBasedOnbranchId(dic['branchId'], dic),
                        modifiedVehicleName(dic['branchId'],dic['activeStatus'], dic),
                        modifiedSlotExist(dic['branchId'],dic),
                        modifiedBranchOption(dic['branchId'],dic)
                        )
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsbasedOnlatAndlng ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchBasedOnlalngandActivstatuandApproval(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails
								,(SQRT(POWER(69.1 * (CAST(bmv.latitude AS DECIMAL(12,7)) - {lat}), 2) + POWER(69.1 * ({lng} - CAST(bmv.longitude AS DECIMAL(12,7))) * COS(bmv.latitude / 57.3), 2))* 1.60934) AS distance           
                                FROM  branchMasterView as bmv
                                WHERE bmv.approvalStatus = ? AND bmv.activeStatus = ? 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(approvalStatus,activeStatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(
                                    modifiedminprice(dic['branchId'],dic), 
                                    getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedVehicleName(dic['branchId'],dic['activeStatus'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic)

                                    )
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchBasedOnlalngandActivstatuandApproval ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0}

async def branchBasedOnlalngandActivstatuandApprovalandOnlineavailability(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        response =  await routers.client.get(f"{os.getenv('BOOKING_URL')}/userSlot?activeStatus={activeStatus}")
        response = json.loads(response.text)
        url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
        slotResponse = await routers.client.get(url)
        slotResponse = json.loads(slotResponse.text)
        slotResp=slotResponse['response']
        if response.get('statusCode') ==1 and slotResponse.get('statusCode') ==1:
            checkBranchSlotIds=response['response']
            response =  await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?checkBranchSlotIds={checkBranchSlotIds}&activeStatus={slotResp}")
            response = json.loads(response.text)
            if response.get('statusCode') ==1 :
                slotRes=response['response']
            else:
                slotRes=[]
        else:
            slotRes=[]
            checkBranchSlotIds=[]
            slotResp=[]
        response =  await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine")
        response = json.loads(response.text)
        if response.get('statusCode') ==1 :
            await db.execute(f"""SELECT CAST((SELECT bm.branchId 
                                         FROM branchMaster AS bm
                                         WHERE bm.branchId NOT IN {(tuple(response['response'])+tuple('0'))}
                             FOR JSON PATH) AS VARCHAR(MAX))""")
            row = await db.fetchone()
            branchRes=[]
            if row[0] != None:
                for i in json.loads(row[0]):
                    branchRes.append(i['branchId'])
            
        else:
            branchRes=[]
        
           
        if len(slotRes)!=0 or len(branchRes)!=0:
            
            await db.execute(f"""SELECT CAST(( SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails
								,(SQRT(POWER(69.1 * (CAST(bmv.latitude AS DECIMAL(12,7)) - {lat}), 2) + POWER(69.1 * ({lng} - CAST(bmv.longitude AS DECIMAL(12,7))) * COS(bmv.latitude / 57.3), 2))* 1.60934) AS distance           
                                FROM  branchMasterView as bmv
                                WHERE bmv.approvalStatus = ? AND bmv.activeStatus = ? AND bmv.onlineBookingAvailability=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(approvalStatus,activeStatus,onlineBookingAvailability))
            row = await db.fetchone()
            
            data=[]
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic={}
                    dic.update(i)
                    await asyncio.gather(modifiedminprice(dic['branchId'], dic), 
                                        getratingsBasedOnbranchId(dic['branchId'], dic),
                                        modifiedVehicleName(dic['branchId'],dic['activeStatus'], dic),
                                        modifiedSlotDetails(dic['branchId'],dic,checkBranchSlotIds,slotResp,activeStatus,branchRes),
                                        modifiedSlotExist(dic['branchId'],dic),
                                        modifiedBranchOption(dic['branchId'],dic)
                                        

                            )
                    data.append(dic)
                return data
            else:
                return {
                "statusCode": 0,
                "response": "Data Not Found"
                
            }
        else:
            return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as branchBasedOnlalngandActivstatuandApprovalandOnlineavailability ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0}

async def branchDetailsbasedOndistrict(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE district= ? 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(district))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic)
                                   )
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsbasedOndistrict ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchDetailsbasedOnstate(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE state= ? 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(state))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic)
                                   )
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsbasedOnstate ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchDetailsbasedOncity(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE city= ? 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(city))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic)
                                   )
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsbasedOncity ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchDetailsbasedOncityandActivestatus(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE city= ? AND bmv.activeStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(city,activeStatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic)
                                   )
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "data":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsbasedOncityandActivestatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchDetailsbasedOnpincode(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
								WHERE pincode= ? 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(pincode))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic)
                                   )
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as branchDetailsbasedOnpincode ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getcitybasedOntype(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        if type=='C':
            await db.execute(f"""SELECT CAST((SELECT DISTINCT ISNULL((bmv.city),'')As city
                                FROM branchMasterView AS bmv
                                FOR JSON PATH) AS VARCHAR(MAX))""")
            row = await db.fetchone()
            if row[0] != None:           
                data=(json.loads(row[0]))
                return {
                "response":data,
                "statusCode":1
                }
            else:
                return {
            "response":"data not found",
            "statusCode":0
            }
        else:                
            return {
                "response":"data not found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as getcitybasedOntype ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def vehicleConfigMasterDetailsbasedOnbranchId(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        if type=='V':
            url=f"{os.getenv('SLOT_SERVICE_URL')}/floorVehicleMaster?branchId={branchId}"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response['statusCode'] == 1:
                data=[] 
                for i in response['response']:               
                    data.append({'vehicleConfigId':i['vehicleType'],
                                'vehicleName':i['vehicleTypeName'],
                                'vehicleImageUrl':i['vehicleImageUrl'],
                                'vehiclePlaceHolderImageUrl':i['vehiclePlaceHolderImageUrl']})         
                return {
                        'statusCode':1,
                        'response':data
                        }
            
        return {
            'statusCode':0,
            'response':"No Data Found"
        }
    except Exception as e:
        print(f'Exception as vehicleConfigMasterDetailsbasedOnbranchId {str(e)}')
        return {}

async def getDetailsBasedOnvehicleType(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        url = f"{os.getenv('SLOT_SERVICE_URL')}/floorVehicleMaster?vehicleType={vehicleType}"
        response = await routers.client.get(url)
        var = json.loads(response.text)
        if var['statusCode'] == 1:       
            for id in var['response']:
                await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                        ((SELECT * FROM branchWorkingHrs AS bwh
                                        WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
                                        ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails
                                        ,(SQRT(POWER(69.1 * (CAST(bmv.latitude AS DECIMAL(12,7)) - {lat}), 2) + POWER(69.1 * (bmv.longitude - CAST({lng} AS DECIMAL(12,7))) * COS(bmv.latitude / 57.3), 2))* 1.60934) AS distance           
                                        FROM  branchMasterView as bmv WHERE bmv.branchId=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""", id['branchId'])
                row = await db.fetchone()
                if row[0] != None:
                    data=json.loads(row[0])                    
                    for dic in data:                        
                        await asyncio.gather(
                                                modifiedminprice(dic['branchId'], dic),
                                                modifiedslots(dic['branchId'], dic), 
                                                getratingsBasedOnbranchId(dic['branchId'], dic),
                                                modifiedSlotExist(dic['branchId'],dic),
                                                modifiedBranchOption(dic['branchId'],dic)

                                                )
            return {
                "response":data,
                "statusCode":1
            }
        else:
            return {
                "response":"data not found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as getDetailsBasedOnvehicleType ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def DetailsBasedOnvehicleTypeandactiveStatusandapproval(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        url = f"{os.getenv('SLOT_SERVICE_URL')}/floorVehicleMaster?vehicleType={vehicleType}"
        response = await routers.client.get(url)
        var = json.loads(response.text)
        if var['statusCode'] == 1:       
            for id in var['response']:
                await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                        ((SELECT * FROM branchWorkingHrs AS bwh
                                        WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
                                        ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails
                                        ,(SQRT(POWER(69.1 * (CAST(bmv.latitude AS DECIMAL(12,7)) - {lat}), 2) + POWER(69.1 * (bmv.longitude - CAST({lng} AS DECIMAL(12,7))) * COS(bmv.latitude / 57.3), 2))* 1.60934) AS distance           
                                        FROM  branchMasterView as bmv WHERE bmv.branchId=? and bmv.approvalStatus=? and bmv.activeStatus=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""", id['branchId'],approvalStatus,activeStatus)
                row = await db.fetchone()
                if row[0] != None:
                    data=json.loads(row[0])                    
                    for dic in data:                        
                        await asyncio.gather(
                                                modifiedminprice(dic['branchId'], dic), 
                                                modifiedslots(dic['branchId'], dic),
                                                getratingsBasedOnbranchId(dic['branchId'], dic),
                                                modifiedSlotExist(dic['branchId'],dic),
                                                modifiedBranchOption(dic['branchId'],dic)
                                                )
            return {
                "response":data,
                "statusCode":1
            }
        else:
            return {
                "response":"data not found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as DetailsBasedOnvehicleTypeandactiveStatusandapproval ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def DetailsBasedOnCityandtype(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        if type=='S':        
            await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                    ((SELECT * FROM branchWorkingHrs AS bwh
                                    WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
                                    ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails,0 As distance                                          
                                    FROM  branchMasterView as bmv WHERE bmv.city=? OR bmv.branchName=? 
                                    FOR JSON PATH) AS VARCHAR(MAX))""",city,city)
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data:                        
                    await asyncio.gather(
                                            modifiedminprice(dic['branchId'], dic),
                                            modifiedslots(dic['branchId'], dic), 
                                            getratingsBasedOnbranchId(dic['branchId'], dic),
                                            modifiedSlotExist(dic['branchId'],dic),
                                            modifiedBranchOption(dic['branchId'],dic)
                                            )
                return {
                    "response":data,
                    "statusCode":1
                }
            else:
                return {
                "response":"data not found",
                "statusCode":0
                }
        else:
            return {
                "response":"data not found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as DetailsBasedOnCityandtype ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def DetailsBasedOnCityandtypeandlatlng(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability,db):
    try:
        if type=='S':        
            await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                    ((SELECT * FROM branchWorkingHrs AS bwh
                                    WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
                                    ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails
                                     ,(SQRT(POWER(69.1 * (CAST(bmv.latitude AS DECIMAL(12,7)) - {lat}), 2) + POWER(69.1 * (bmv.longitude - CAST({lng} AS DECIMAL(12,7))) * COS(bmv.latitude / 57.3), 2))* 1.60934) AS distance                                          
                                    FROM  branchMasterView as bmv WHERE bmv.city=? OR bmv.branchName=? 
                                    FOR JSON PATH) AS VARCHAR(MAX))""",city,city)
            row = await db.fetchone()
            if row[0] != None:
                data=json.loads(row[0])                    
                for dic in data:                        
                    await asyncio.gather(
                                            modifiedminprice(dic['branchId'], dic),
                                            modifiedslots(dic['branchId'], dic), 
                                            getratingsBasedOnbranchId(dic['branchId'], dic),
                                            modifiedSlotExist(dic['branchId'],dic),
                                            modifiedBranchOption(dic['branchId'],dic)
                                            )
                return {
                    "response":data,
                    "statusCode":1
                }
            else:
                return {
                "response":"data not found",
                "statusCode":0
                }
        else:
            return {
                "response":"data not found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as DetailsBasedOnCityandtypeandlatlng ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def getbranchDetails(parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bmv.*,ISNULL
                                ((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bmv.branchId FOR JSON PATH),'[]') as branchWorkingHour,
								ISNULL((SELECT * FROM branchImageMaster WHERE branchId=bmv.branchId FOR JSON PATH),'[]')AS branchImageMasterDetails          
                                FROM  branchMasterView as bmv 
                                FOR JSON PATH) AS VARCHAR(MAX))""")
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            for dic in data:
                await asyncio.gather(getratingsBasedOnbranchId(dic['branchId'], dic),
                                    modifiedSlotExist(dic['branchId'],dic),
                                    modifiedBranchOption(dic['branchId'],dic)
                                   )
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getbranchDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }



branchDict = {
    "parkingOwnerId=True, activeStatus=False, approvalStatus=False, branchId=False, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsbasedOnparkingOwnerId,
	"parkingOwnerId=True, activeStatus=True, approvalStatus=False, branchId=False, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":DetailsbasedOnparkingOwnerIdandactiveStatus,
	"parkingOwnerId=True, activeStatus=True, approvalStatus=True, branchId=False, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":DetailsOnparkingOwnerIdandactiveStatusandapprovalStatus,
	"parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=True, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsbasedOnbranchId,
	"parkingOwnerId=False, activeStatus=True, approvalStatus=False, branchId=True, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsbasedOnbranchIdandactiveStatus,
	"parkingOwnerId=False, activeStatus=True, approvalStatus=True, branchId=True, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":DetailsOnbranchIdandactiveStatusandapprovalStatus,
	"parkingOwnerId=False, activeStatus=False, approvalStatus=True, branchId=False, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsbasedOnapprovalStatus,
	"parkingOwnerId=False, activeStatus=True, approvalStatus=False, branchId=False, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsbasedOnactiveStatus,
    "parkingOwnerId=False, activeStatus=True, approvalStatus=True, branchId=False, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsBasedOnApprovalActiveStatus,
	"parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=False, lat=True, lng=True, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsbasedOnlatAndlng,
    "parkingOwnerId=False, activeStatus=True, approvalStatus=True, branchId=False, lat=True, lng=True, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchBasedOnlalngandActivstatuandApproval,
    "parkingOwnerId=False, activeStatus=True, approvalStatus=True, branchId=False, lat=True, lng=True, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=True":branchBasedOnlalngandActivstatuandApprovalandOnlineavailability,
	"parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=False, lat=False, lng=False, district=True, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsbasedOndistrict,
	"parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=False, lat=False, lng=False, district=False, state=True, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsbasedOnstate,
	"parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=False, lat=False, lng=False, district=False, state=False, city=True, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsbasedOncity,
    "parkingOwnerId=False, activeStatus=True, approvalStatus=False, branchId=False, lat=False, lng=False, district=False, state=False, city=True, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsbasedOncityandActivestatus,
	"parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=False, lat=False, lng=False, district=False, state=False, city=False, pincode=True, type=False, vehicleType=False, onlineBookingAvailability=False":branchDetailsbasedOnpincode,
	"parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=False, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=True, vehicleType=False, onlineBookingAvailability=False":getcitybasedOntype,
    "parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=True, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=True, vehicleType=False, onlineBookingAvailability=False":vehicleConfigMasterDetailsbasedOnbranchId,
    "parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=False, lat=True, lng=True, district=False, state=False, city=False, pincode=False, type=False, vehicleType=True, onlineBookingAvailability=False":getDetailsBasedOnvehicleType,
    "parkingOwnerId=False, activeStatus=True, approvalStatus=True, branchId=False, lat=True, lng=True, district=False, state=False, city=False, pincode=False, type=False, vehicleType=True, onlineBookingAvailability=False":DetailsBasedOnvehicleTypeandactiveStatusandapproval,
    "parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=False, lat=False, lng=False, district=False, state=False, city=True, pincode=False, type=True, vehicleType=False, onlineBookingAvailability=False":DetailsBasedOnCityandtype,
    "parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=False, lat=True, lng=True, district=False, state=False, city=True, pincode=False, type=True, vehicleType=False, onlineBookingAvailability=False":DetailsBasedOnCityandtypeandlatlng,
	"parkingOwnerId=False, activeStatus=False, approvalStatus=False, branchId=False, lat=False, lng=False, district=False, state=False, city=False, pincode=False, type=False, vehicleType=False, onlineBookingAvailability=False":getbranchDetails
}

##################################################################################################################
@router.get('')
async def branchGet(parkingOwnerId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),approvalStatus:Optional[str]=Query(None),branchId:Optional[int]=Query(None),lat:Optional[float]=Query(None),lng:Optional[float]=Query(None),district:Optional[str]=Query(None),state:Optional[str]=Query(None),city:Optional[str]=Query(None),pincode:Optional[int]=Query(None),type:Optional[str]=Query(None),vehicleType:Optional[int]=Query(None),onlineBookingAvailability:Optional[str]=Query(None), db:Cursor = Depends(get_cursor)):
    try:
        st = f"parkingOwnerId={True if parkingOwnerId else False}, activeStatus={True if activeStatus else False}, approvalStatus={True if approvalStatus else False}, branchId={True if branchId else False}, lat={True if lat else False}, lng={True if lng else False}, district={True if district else False}, state={True if state else False}, city={True if city else False}, pincode={True if pincode else False}, type={True if type else False}, vehicleType={True if vehicleType else False}, onlineBookingAvailability={True if onlineBookingAvailability else False}"
        return await branchDict[st](parkingOwnerId,activeStatus,approvalStatus,branchId,lat,lng,district,state,city,pincode,type,vehicleType,onlineBookingAvailability, db)
    except Exception as e:
        print("Exception as branchGet ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


@router.post('')
async def postbranchMaster(request:schemas.BranchMaster,db: Cursor = Depends(get_cursor)):
    try:
        if request.branchImageMasterDetails!=None:
                    branchImageMasterJson = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.branchImageMasterDetails)
                    branchImageMasterJson=json.dumps(branchImageMasterJson,indent=4, sort_keys=True, default=str)
        else:
            branchImageMasterJson=None
        if request.branchWorkingHrsDetails:
            branchWorkingHrsJson= Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.branchWorkingHrsDetails)
            branchWorkingHrsJson=json.dumps(branchWorkingHrsJson,indent=4, sort_keys=True, default=str)
        else:
            branchWorkingHrsJson=None
        await db.execute(f""" EXEC [dbo].[postBranchMaster]
                                    @parkingOwnerId =?,
									@branchName =?,
                                    @shortName=?,
									@latitude =?,
									@longitude =?,
									@address1 =?,
									@address2 =?,
									@district =?,
									@state =?,
									@city =?,
									@pincode =?,
									@phoneNumber =?,
									@alternatePhoneNumber =?,
									@emailId =?,
									@licenseNo =?,
									@licensePeriodFrom =?,
									@licensePeriodTo =?,
									@license =?,
									@document1 =?,
									@document2 =?,
									@multiBook =?,
									@activeStatus =?,
									@approvalStatus =?,
                                    @onlineBookingAvailability=?,
                                    @isPayBookAvailable=?,
									@isBookCheckInAvailable=?,
									@isPayAtCheckoutAvailable=?,
									@isPayLaterAvaialble=?,
									@advanceBookingHourOrDayType=?,
									@advanceBookingHourOrDay =?,
									@advanceBookingCharges=?,
									@minHour =?,
									@maxHour =?,
									@minDay =?,
									@maxDay =?,
									@createdBy =?,
         							@branchWorkingHrsJson=?,
									@branchImageMasterJson=?""",
                                    (
                                    request.parkingOwnerId,
									request.branchName,
                                    request.shortName,
									request.latitude,
									request.longitude,
									request.address1,
									request.address2,
									request.district,
									request.state,
									request.city,
									request.pincode,
									request.phoneNumber,
									request.alternatePhoneNumber,
									request.emailId,
									request.licenseNo,
									request.licensePeriodFrom,
									request.licensePeriodTo,
									request.license,
									request.document1,
									request.document2,
									request.multiBook,
									request.activeStatus,
									request.approvalStatus,
                                    request.onlineBookingAvailability,
									request.isPayBookAvailable,
									request.isBookCheckInAvailable,
									request.isPayAtCheckoutAvailable,
									request.isPayLaterAvaialble,
									request.advanceBookingHourOrDayType,
									request.advanceBookingHourOrDay,
									request.advanceBookingCharges,
									request.minHour,
									request.maxHour,
									request.minDay,
									request.maxDay,
									request.createdBy,
									branchWorkingHrsJson,
									branchImageMasterJson
                                    ))

        rows=await db.fetchone()
        await db.commit()
        if rows[1]==1:
            postBranchName.delay(int(rows[2]),request.branchName)
            return{
                "statusCode":int(rows[1]),
                "response":rows[0]
            }
        return{
                "statusCode":int(rows[1]),
                "response":rows[0]
            }
    except Exception as e:
        print("Exception as postbranchMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
    
@router.put('')
async def putbranchMaster(request:schemas.PutBranchMaster,db: Cursor = Depends(get_cursor)):
    try:
        if request.branchWorkingHrs!=None:                
                    branchWorkingHrsDetails = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.branchWorkingHrs)
                    branchWorkingHrsDetails=json.dumps(branchWorkingHrsDetails,indent=4, sort_keys=True, default=str)
        else:
            branchWorkingHrsDetails=None
        if request.branchImageMasterDetails!=None:
            branchImageMasterDetails = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.branchImageMasterDetails)
            branchImageMasterDetails=json.dumps(branchImageMasterDetails,indent=4, sort_keys=True, default=str)
        else:
            branchImageMasterDetails=None
        await db.execute(f"""EXEC [dbo].[putBranchMaster]
                                    @branchId=?,
                                    @parkingOwnerId =?,
									@branchName =?,
                                    @shortName=?,
									@latitude =?,
									@longitude =?,
									@address1 =?,
									@address2 =?,
									@district =?,
									@state =?,
									@city =?,
									@pincode =?,
									@phoneNumber =?,
									@alternatePhoneNumber =?,
									@emailId =?,
									@licenseNo =?,
									@licensePeriodFrom =?,
									@licensePeriodTo =?,
									@license =?,
									@document1 =?,
									@document2 =?,
									@multiBook =?,
									@approvalStatus =?,
									@onlineBookingAvailability=?,
                                    @isPayBookAvailable=?,
									@isBookCheckInAvailable=?,
									@isPayAtCheckoutAvailable=?,
									@isPayLaterAvaialble=?,
									@advanceBookingHourOrDayType=?,
									@advanceBookingHourOrDay =?,
									@advanceBookingCharges=?,
									@minHour =?,
									@maxHour =?,
									@minDay =?,
									@maxDay =?,
									@updatedBy =?,
									@branchWorkingHrsJson =?,
									@branchImageMasterJson =?""",
                                    (
                                    request.branchId,
                                    request.parkingOwnerId,
									request.branchName,
                                    request.shortName,
									request.latitude,
									request.longitude,
									request.address1,
									request.address2,
									request.district,
									request.state,
									request.city,
									request.pincode,
									request.phoneNumber,
									request.alternatePhoneNumber,
									request.emailId,
									request.licenseNo,
									request.licensePeriodFrom,
									request.licensePeriodTo,
									request.license,
									request.document1,
									request.document2,
									request.multiBook,
									request.approvalStatus,
									request.onlineBookingAvailability,
									request.isPayBookAvailable,
									request.isBookCheckInAvailable,
									request.isPayAtCheckoutAvailable,
									request.isPayLaterAvaialble,
									request.advanceBookingHourOrDayType,
									request.advanceBookingHourOrDay,
									request.advanceBookingCharges,
									request.minHour,
									request.maxHour,
									request.minDay,
									request.maxDay,
									request.updatedBy,
									branchWorkingHrsDetails,
									branchImageMasterDetails
                                    
                                    ))
        rows=await db.fetchone()
        await db.commit()
        if int(rows[1])==1:
            postBranchName.delay(request.branchId,request.branchName)
            return{
                "statusCode":int(rows[1]),
                "response":rows[0]
            }
        return{
                "statusCode":int(rows[1]),
                "response":rows[0]
            }
    except Exception as e:
        print("Exception as putbranchMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.delete('')
async def deletebranchMaster(branchId:int,activeStatus:str,db: Cursor=Depends(get_cursor)):
    try:
        result=await db.execute(f"""UPDATE branchMaster SET activeStatus=? WHERE branchId=?""",(activeStatus,branchId))
        await db.commit()
        if result.rowcount>=1:
            if activeStatus=="D":
                return{
            "statusCode": 1,
            "response": "Deactivated Successfully"
        }
            else:
                return{
            "statusCode": 1,
            "response": "Activated Successfully"
        }
        else:
            return {
            "statusCode": 0,
            "response": "Data Not Deleted"}
    except Exception as e:
        print("Exception as deletebranchMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }	

	

    



