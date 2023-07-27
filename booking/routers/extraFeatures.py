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
from routers.config import get_cursor
# from task import passlot
import time
import json,os 
import asyncio
from dotenv import load_dotenv
load_dotenv()

router=APIRouter(prefix='/extraFeatures',tags=["extraFeatures"])

async def getExtraFeaturesDetails(floorFeaturesId,dic):
    try:
        url = f"{os.getenv('SLOT_SERVICE_URL')}/floorfeatures?featuresId={floorFeaturesId}"
        response = await routers.client.get(url)
        res= json.loads(response.text)
        if res['statusCode']==1:
            dic['featureName']=res['response'][0]['featureName']
            dic['tax']=res['response'][0]['tax']
            dic['totalAmount']=res['response'][0]['totalAmount']
        else:
            dic['featureName']=""
            dic['tax']=""
            dic['totalAmount']=""
    except Exception as e:
        print("Exception as getExtraFeaturesDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
async def bookingPassIdDetails(floorFeaturesId,bookingPassId,db):
    try:
       
        await db.execute(f"""SELECT CAST((SELECT ef.* 
                                            FROM extraFeatures as ef 
                                            WHERE ef.bookingPassId=? AND ef.bookingIdType='P'
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(bookingPassId))
        row = await db.fetchone()
        data=[]
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await getExtraFeaturesDetails(i['floorFeaturesId'],dic)
                data.append(dic)
            return {
                "response":data,
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as ExtraFeatures bookingPassIdDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getextraFeaturesbasedonfloorFeaturesIdPassId(floorFeaturesId,bookingPassId,db):
    try:
        data = []
        url2 = f"{os.getenv('SLOT_SERVICE_URL')}/floorfeatures?featuresId={floorFeaturesId}"
        response2 = await routers.client.get(url2)
        var2= json.loads(response2.text)
        if var2['statusCode']==1:   
            for id in var2['response'] :              
                await db.execute(f"""
                                    SELECT CAST((SELECT (CAST((ISNULL((ISNULL(bv.totalAmount, 0) - ISNULL((SELECT SUM({id['totalAmount']}*ef.count) as amt FROM extraFeatures as ef 
                                    WHERE ef.bookingPassId = bv.bookingId AND ef.bookingIdType = 'B'), 0) - 
                                    ISNULL((SELECT SUM(ef.extraFee) FROM extraFees as ef WHERE ef.bookingPassId = bv.bookingId AND ef.bookingIdType = 'B'),0)),0))AS DECIMAL(7,2))) AS boookingAmount,
                                    CAST((ISNULL((ISNULL(bv.taxAmount, 0) - ISNULL((SELECT SUM({id['tax']}*ef.count) as amt FROM extraFeatures as ef 
                                    WHERE ef.bookingPassId = bv.bookingId AND ef.bookingIdType = 'B'), 0)),0)) AS DECIMAL(7,2)) as bookingTax
                                    FROM booking as bv
                                    WHERE bv.bookingId=? 
                                    FOR JSON PATH) AS VARCHAR(MAX))
                                    """,(bookingPassId))
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
    except Exception as e:
        print(f'Exception as getextraFeaturesbasedonfloorFeaturesIdPassId {str(e)}')
        return {
            "response": str(e),
            "statusCode": 0
        }

async def getExtraFeaturesFloorFeaturesId(floorFeaturesId,bookingPassId,db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT ef.* 
                                            FROM extraFeatures as ef 
                                            WHERE ef.floorFeaturesId=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(floorFeaturesId))
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
        print("Exception as getExtraFeaturesFloorFeaturesId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


    
extraFeaturesDict = {
    "floorFeaturesId=True, bookingPassId=True":getextraFeaturesbasedonfloorFeaturesIdPassId,
    "floorFeaturesId=False, bookingPassId=True":bookingPassIdDetails,
    "floorFeaturesId=True, bookingPassId=False":getExtraFeaturesFloorFeaturesId

}

@router.get('')
async def getExtraFeatures(floorFeaturesId:Optional[int]=Query(None),bookingPassId:Optional[int]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"floorFeaturesId={True if floorFeaturesId else False}, bookingPassId={True if bookingPassId else False}"
        return await extraFeaturesDict[st](floorFeaturesId, bookingPassId, db)
    except Exception as e:
        print("Exception as getExtraFeatures ",str(e))
        return{
        "statusCode": 0,
        "response":"Server Error"    
        }

@router.post('')
async def postExtraFeatures(request:schemas.PostExtraFeatures,db:Cursor=Depends(get_cursor)):
    try:
        url = f"{os.getenv('SLOT_SERVICE_URL')}/floorfeatures?featuresId={request.floorFeaturesId}"
        response = await routers.client.get(url)  
        var = json.loads(response.text)
        if var['statusCode'] == 1:
            for id in var['response']:
                await db.execute(f"""EXEC [dbo].[postextraFeatures]
                                                @bookingPassId =?,
                                                @bookingIdType=?,
                                                @floorFeaturesId =?,
                                                @count=?,
                                                @extraDetail =?
                                                """,
                                            (request.bookingPassId,
                                            request.bookingIdType,
                                            request.floorFeaturesId,
                                            request.count,
                                            request.extraDetail  
                                            )
                                            )
               
               
                row=await db.fetchone()
                await db.commit()               
                if row[1]==1:
                    result=await db.execute(f"""UPDATE booking SET totalAmount=ISNULL((SELECT totalAmount FROM booking WHERE bookingId=?),0.0)+{id['totalAmount']} WHERE bookingId=?""",(request.bookingPassId,request.bookingPassId))                    
                    await db.commit()
                    if result.rowcount>=1:
                        return{
                        "statusCode": 1,
                        "response": "Data Added Successfully"
                        }
                    else:
                        return{
                            "statusCode": 0,
                            "response": "Data Not Updated in Booking"
                        }
                else:
                    return{
                    "statusCode": 0,
                    "response": "Data Not Added in ExtraFeatures"  
                    }
        else:
            return{
            "statusCode": 0,
            "response": "Data Not Added"
        }                                        
    except Exception as e:
        print("Exception as postExtraFeatures ",str(e))
        return{
        "statusCode": 0,
        "response":"Server Error"    
        }


@router.put('')
async def putExtraFeatures(extraFeatureId:int,extraDetail:str,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putExtraFeatures] ?,?""",(extraFeatureId,extraDetail))
        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as putExtraFeatures ",str(e))
        return{
        "statusCode": 0,
        "response":"Server Error"    
        }