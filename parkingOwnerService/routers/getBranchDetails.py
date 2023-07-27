from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from fastapi import Response
from aioodbc.cursor import Cursor
from routers.eventsServer import publish
import routers
from routers.config import get_cursor
from task import passlot
from typing import Optional
from fastapi import Query
from datetime import time,date
import datetime
import json,os
import asyncio
import ast
from dotenv import load_dotenv
load_dotenv()

dateTimeRouter = APIRouter(prefix="/getBranchBasedOnDateTime",tags=['branchMaster'])


async def getRatings(branchId,dic):
    try:
        url=f"{os.getenv('USER_SERVICE_URL')}/feedBackMaster?branchId={branchId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        rating=[]
        if response.get('statusCode') == 1:
            for i in response['response']:                 
                rating.append(i['feedbackRating'])
            avg = sum(rating) / len(rating)        
            dic['rating']=avg
        else:
            dic['rating']=0        
    except Exception as e:
        print("Exception as getRatings",str(e))
        return ""

async def getPriceDetails(branchId):
    try:
        url=f"{os.getenv('SLOT_SERVICE_URL')}/priceMaster?branchId={branchId}&idType=V"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response.get('statusCode') == 1:
            return response['response'][0]['minPrice']
        return 0
    except Exception as e:
        print("Exception as getPriceDetails ",str(e))
        return ""

async def getSlotExist(branchId):
    try:
        url=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?slotExist={branchId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response.get('statusCode') == 1:
            return response['response'][0]['slotExist']
        return ""
    except Exception as e:
        print("Exception as getSlotExist ",str(e))
        return ""

async def getSlotDetails(branchId,checkBranchSlotIds,vehicleType,slotResponse):
    try:
        url=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?branchId={branchId}&activeStatus={slotResponse}&checkBranchSlotIds={checkBranchSlotIds}&typeOfVehicle={vehicleType}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response.get('statusCode') == 1:
            return response['response'][0]['parkingSlotIdCount']
        return 0
    except Exception as e:
        print("Exception as getSlotDetails ",str(e))
        return ""

async def getTotalSlotDetails(branchId,slotResponse):
    try:
        url=f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?branchId={branchId}&activeStatus={slotResponse}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response.get('statusCode') == 1:
            return response['response'][0]['totalSlot']
        return 0
    except Exception as e:
        print("Exception as getTotalSlotDetails ",str(e))
        return ""

async def getBranchSlotDetails(branchId,vehicleType,fromDate,toDate,fromTime,toTime):
    try:
        url=f"{os.getenv('SLOT_SERVICE_URL')}/floorVehicleMaster?branchId={branchId}&vehicleType={vehicleType}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        
        if response.get('statusCode') == 1:
            floorVehicleCapacity=response['response']
            url=f"{os.getenv('BOOKING_URL')}/booking?fromDate={datetime.datetime.combine(fromDate,datetime.time(0,0,0))}&toDate={datetime.datetime.combine(toDate,datetime.time(0,0,0))}&fromTime={fromTime}&toTime={toTime}&category={vehicleType}&branchId={branchId}"
            response = await routers.client.get(url)
            response = json.loads(response.text)
            if response.get('statusCode') == 1:
                slotCapacity=response['response']
                return slotCapacity[0]['slotCapacity'] - floorVehicleCapacity[0]['capacity']
            
        return 0
    except Exception as e:
        print("Exception as getBranchSlotDetails ",str(e))
        return ""



async def modifiedPriceDetails(branchId,dic):
    dic['minprice']=await getPriceDetails(branchId)
   
async def modifiedSlotDetails(branchId,dic,checkBranchSlotIds,vehicleType,slotResponse,branchRes,fromDate,toDate,fromTime,toTime):
    if branchId not in branchRes:
        dic['slotAvailable']=await getSlotDetails(branchId,checkBranchSlotIds,vehicleType,slotResponse)
    else:
       dic['slotAvailable']=await getBranchSlotDetails(branchId,vehicleType,fromDate,toDate,fromTime,toTime) 

async def modifiedTotalSlotDetails(branchId,dic,slotResponse):
    
    dic['totalSlot']=await getTotalSlotDetails(branchId,slotResponse)

async def modifiedSlotExist(branchId,dic):
    
    dic['slotExist']=await getSlotExist(branchId)

async def getDateTimeBasedDetails(fromDate,toDate,fromTime,toTime,lat,lng,vehicleType,db):
    try:
        response =  await routers.client.get(f"{os.getenv('BOOKING_URL')}/booking?fromDate={datetime.datetime.combine(fromDate,datetime.time(0,0,0))}&toDate={datetime.datetime.combine(toDate,datetime.time(0,0,0))}&fromTime={fromTime}&toTime={toTime}")
        response = json.loads(response.text)
        url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
        slotResponse = await routers.client.get(url)
        slotResponse = json.loads(slotResponse.text)
        slotResp=slotResponse['response']
        if response.get('statusCode') ==1 and slotResponse.get('statusCode') ==1:
            checkBranchSlotIds=response['response']
            response =  await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?checkBranchSlotIds={checkBranchSlotIds}&typeOfVehicle={vehicleType}&activeStatus={slotResp}")
            response = json.loads(response.text)
            if response.get('statusCode') ==1 :
                slotRes=response['response']
            else:
                slotRes=[]
        else:
            slotRes=[]
            checkBranchSlotIds=[]
            slotResp=[]
        response =  await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/parkingLotLine?typeOfVehicle={vehicleType}")
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
            
            await db.execute(f"""SELECT CAST(( SELECT * FROM (SELECT bm.*,cast((SQRT(POWER(69.1 * (CAST(bm.latitude AS DECIMAL(12,7)) - {lat}), 2) 
                                + POWER(69.1 * ({lng} - CAST(bm.longitude AS DECIMAL(12,7))) * 
                                COS(bm.latitude / 57.3), 2))* 1.60934) as decimal(12,7)) AS distance,
                                            (SELECT * FROM branchImageMaster WHERE branchImageMaster.branchId = bm.branchId FOR JSON PATH)as branchImages
                                            FROM branchMaster AS bm
                                            WHERE branchId IN {tuple(set(branchRes+slotRes))+tuple('0')}
                                                    AND approvalStatus = 'A' AND onlineBookingAvailability='Y'  
                                                    AND bm.activeStatus = 'A') as mainTab
                                WHERE distance <= 5
                                FOR JSON PATH) AS VARCHAR(MAX))""")
            row = await db.fetchone()
            
            data=[]
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic={}
                    dic.update(i)
                    await asyncio.gather(modifiedPriceDetails(dic['branchId'],dic),
                                        getRatings(dic["branchId"],dic),
                                        modifiedSlotDetails(dic['branchId'],dic,checkBranchSlotIds,vehicleType,slotResp,branchRes,fromDate,toDate,fromTime,toTime),
                                        modifiedSlotExist(dic['branchId'],dic),
                                        modifiedTotalSlotDetails(dic['branchId'],dic,slotResp)
                                        

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
        print("Exception as getDateTimeBasedDetails ",str(e))
        return ""

@dateTimeRouter.get('')
async def getBranchDateTime(vehicleType:int,fromDate:Optional[date]=Query(None),toDate:Optional[date]=Query(None),fromTime:Optional[time]=Query(None),toTime:Optional[time]=Query(None),lat:Optional[float]=Query(None),lng:Optional[float]=Query(None), db:Cursor = Depends(get_cursor)):
    try:

        if fromDate!=None and toDate!=None and fromTime!=None and toTime!=None:
            branchDateTimeDetails=await getDateTimeBasedDetails(fromDate,toDate,fromTime,toTime,lat,lng,vehicleType,db)
            return branchDateTimeDetails
        else:
            return {
                "statusCode": 0,
                "response": "Data Not Found"
                
            }
               
    except Exception as e:
        print("Exception as getBranchDateTime ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }