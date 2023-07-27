from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from fastapi import Response
from aioodbc.cursor import Cursor
from routers.eventsServer import publish
import schemas,os
import routers
# from routers.config import engine 
from routers.config import get_cursor
from task import passlot
from typing import Optional
from fastapi import Query
import time
import json 
import asyncio
from dotenv import load_dotenv
load_dotenv()


router = APIRouter(prefix="/parkingOwnerMaster",tags=['parkingOwnerMaster'])

async def getUserDetailsBasedOnUserId(userId):
    try:
        url=f"{os.getenv('USER_SERVICE_URL')}/userMaster?userId={userId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:
                return {
                            'userName':i['userName'],
                            'emailId':i['emailId'],
                            'phoneNumber':i['phoneNumber'],
                            'imageUrl':i['imageUrl'],
                            'approvalStatus':i['approvalStatus'],
                            'userMasterActiveStatus':i['activeStatus'],
                            'password':i['password']
                        }
        return {}
    except Exception as e:
        print("Exception as getUserDetailsBasedOnUserId ",str(e))
        return {}

async def getAddressDetails(userId):
    try:
        url = f"{os.getenv('USER_SERVICE_URL')}/addressMaster?userId={userId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:
                return {
                        'addressId':i['addressId'],
                        'address':i['address'],
                        'alternatePhoneNumber':i['alternatePhoneNumber'],
                        'city':i['city'],
                        'district':i['district'],
                        'pincode':i['pincode'],
                        'state':i['state']
                    }

        return []
    except Exception as e:
        print("Exception as getAddressDetails ",str(e))
        return []

    

async def modifiedDataUserDetails(userId, dic):
    res  = await getUserDetailsBasedOnUserId(userId)
    dic.update(res)
    

async def modifiedDataAddressDetails(userId, dic):
    res  = await getAddressDetails(userId)
    dic['addressDetais'] = res



    
async def getDetailsBasedOnUserId(userId,parkingOwnerId,activeStatus,type,city, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pom.*,ISNULL
                                ((SELECT bm.*,ISNULL((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bm.branchId FOR JSON PATH),'[]') as branchWorkingHour
                                FROM branchMaster as bm WHERE bm.parkingOwnerId = pom.parkingOwnerId FOR JSON PATH),'[]') as branchDetails
                                FROM  parkingOwnerMaster as pom WHERE pom.userId = ?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (userId))
        row = await db.fetchone()
        if row[0] != None:
            data=json.loads(row[0])
            for dic in data:
                await asyncio.gather(
                                        modifiedDataUserDetails(dic['userId'], dic), 
                                        modifiedDataAddressDetails(dic['userId'], dic)
                                        )
            return {
                "response":data,
                "statusCode":1
            }

        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnUserId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnparkingOwnerId(userId,parkingOwnerId,activeStatus,type,city, db):
    dic = {}
    try:
        row=await db.execute(f"""SELECT CAST((SELECT pom.*,ISNULL
                                ((SELECT bm.*,ISNULL((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bm.branchId FOR JSON PATH),'[]') as branchWorkingHour
                                FROM branchMaster as bm WHERE bm.parkingOwnerId = pom.parkingOwnerId FOR JSON PATH),'[]') as branchDetails
                                FROM  parkingOwnerMaster as pom WHERE pom.parkingOwnerId = ?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (parkingOwnerId))
        row = await db.fetchone()
        if row[0] != None:
            data=json.loads(row[0])                    
            for dic in data:
                await asyncio.gather(
                                        modifiedDataUserDetails(dic['userId'], dic), 
                                        modifiedDataAddressDetails(dic['userId'], dic)
                                        )

            return {
                "response":data,
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnparkingOwnerId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnactiveStatus(userId,parkingOwnerId,activeStatus,type,city, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pom.*,ISNULL
                                ((SELECT bm.*,ISNULL((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bm.branchId FOR JSON PATH),'[]') as branchWorkingHour
                                FROM branchMaster as bm WHERE bm.parkingOwnerId = pom.parkingOwnerId FOR JSON PATH),'[]') as branchDetails
                                FROM  parkingOwnerMaster as pom WHERE pom.activeStatus= ?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            data=json.loads(row[0])
            for dic in data:
                await asyncio.gather(
                                        modifiedDataUserDetails(dic['userId'], dic), 
                                        modifiedDataAddressDetails(dic['userId'], dic)
                                        )
            return {
                "response":data,
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnactiveStatusUserId(userId,parkingOwnerId,activeStatus,type,city, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pom.*,ISNULL
                                ((SELECT bm.*,ISNULL((SELECT * FROM branchWorkingHrs AS bwh
                                WHERE bwh.branchId = bm.branchId FOR JSON PATH),'[]') as branchWorkingHour
                                FROM branchMaster as bm WHERE bm.parkingOwnerId = pom.parkingOwnerId FOR JSON PATH),'[]') as branchDetails
                                FROM  parkingOwnerMaster as pom WHERE pom.activeStatus= ? AND pom.userId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (activeStatus,userId))
        row = await db.fetchone()
        if row[0] != None:
            data=json.loads(row[0])
            for dic in data:
                await asyncio.gather(
                                        modifiedDataUserDetails(dic['userId'], dic), 
                                        modifiedDataAddressDetails(dic['userId'], dic)
                                        )
            return {
                "response":data,
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnactiveStatusUserId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnpassType(userId,parkingOwnerId,activeStatus,type,city, db):
    
    try:
        data=[]
        if type=='P':
            url = f"{os.getenv('PARKING_PASS_MODULE_URL')}/parkingPassConfig?activeStatus=A"
            response = await routers.client.get(url)  
            var = json.loads(response.text)
            if var['statusCode'] == 1:
        
                for id in var['response']:
                    await db.execute(f"""SELECT CAST((SELECT DISTINCT bm.* 
                                            FROM parkingOwnerView AS pov
                                            INNER JOIN branchMaster AS bm
                                            ON bm.parkingOwnerId = pov.parkingOwnerId AND bm.branchId=?
                                            WHERE pov.activeStatus=? 
                                            FOR JSON PATH) AS VARCHAR(MAX))""",(id['branchId'],activeStatus))
                    row = await db.fetchone()
                    if row[0] != None:
                        for i in json.loads(row[0]):
                            dic = {}
                            dic.update(i)                  
                            data.append(dic)
                if len(data)!=0:
                    return {
                    "response":data,
                    "statusCode":1
                    }
                else:
                    return {
                        "response":"Data Not Found",
                        "statusCode":0
                      }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnpassType ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnpassTypeandcity(userId,parkingOwnerId,activeStatus,type,city, db):
    data=[]
    try:
        if type=='P':
            url1 = f"{os.getenv('PARKING_PASS_MODULE_URL')}/parkingPassConfig?activeStatus=A"
            response1 = await routers.client.get(url1)

            url2 = f"{os.getenv('USER_SERVICE_URL')}/addressMaster"
            response2 = await routers.client.get(url2)
            
            var1 = json.loads(response1.text)
            
            var2 = json.loads(response2.text)
           
            if var1['statusCode']==1 and var2['statusCode']==1:   
                for id in var1['response'] :
                    for id1 in var2['response']:
                        await db.execute(f"""SELECT CAST((SELECT DISTINCT bm.*,pov.logoUrl
                                                FROM parkingOwnerView AS pov
                                                INNER JOIN branchMaster AS bm
                                                ON bm.parkingOwnerId = pov.parkingOwnerId AND bm.branchId=? AND pov.userId=?
                                                WHERE bm.city=? 
                                                FOR JSON PATH) AS VARCHAR(MAX))""",id['branchId'],id1['userId'],city)
                        row = await db.fetchone()                        
                        if row[0] != None:
                            data.append(json.loads(row[0]))
                if len(data)!=0:
                    return {
                    "response":data,
                    "statusCode":1
                    }
                else:
                    return {
                            "response":"Data Not Found",
                            "statusCode":0
                            }                        
            else:
                return {
                        "response":"Data Not Found",
                        "statusCode":0
                        }

        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getDetailsBasedOnpassTypeandcity ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getParkingOwnerDetails(userId,parkingOwnerId,activeStatus,type,city, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pom.*                               
                                FROM  parkingOwnerMaster as pom 
                                FOR JSON PATH) AS VARCHAR(MAX))""")
        row = await db.fetchone()
        if row[0] != None:
            data=json.loads(row[0])
            for dic in data:
                await asyncio.gather(
                                        modifiedDataUserDetails(dic['userId'], dic), 
                                        modifiedDataAddressDetails(dic['userId'], dic)
                                        )
            return {
                "response":data,
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getParkingOwnerDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


parkingOwnwerDic = {

    "userId=True,parkingOwnerId=False,activeStatus=False,type=False,city=False": getDetailsBasedOnUserId,
    "userId=False,parkingOwnerId=True,activeStatus=False,type=False,city=False":getDetailsBasedOnparkingOwnerId,
    "userId=False,parkingOwnerId=False,activeStatus=True,type=False,city=False":getDetailsBasedOnactiveStatus,
    "userId=True,parkingOwnerId=False,activeStatus=True,type=False,city=False":getDetailsBasedOnactiveStatusUserId,
    "userId=False,parkingOwnerId=False,activeStatus=True,type=True,city=False":getDetailsBasedOnpassType,
    "userId=False,parkingOwnerId=False,activeStatus=False,type=True,city=True":getDetailsBasedOnpassTypeandcity,
    "userId=False,parkingOwnerId=False,activeStatus=False,type=False,city=False":getParkingOwnerDetails
    
}

@router.get('')
async def getParkingOwner(userId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),type:Optional[str]=Query(None),city:Optional[str]=Query(None),db: Cursor = Depends(get_cursor)):
    try:
        st = f"userId={True if userId else False},parkingOwnerId={True if parkingOwnerId else False},activeStatus={True if activeStatus else False},type={True if type else False},city={True if city else False}"
        return await parkingOwnwerDic[st](userId,parkingOwnerId,activeStatus,type,city,db)
    except Exception as e:
        print("Exception as getParkingOwner ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


@router.post('')
async def parkingOwnerMaster(request:schemas.PostparkingOwner,db: Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postParkingOwnerMaster]
                                            @userId=?,
                                            @parkingName=?,
                                            @shortName=?,
                                            @founderName=?,
                                            @logoUrl=?,
                                            @websiteUrl=?,
                                            @gstNumber=?,
                                            @placeType=?,
                                            @activeStatus=?,
                                            @createdBy=?
                                            """,
                                            (request.userId,
                                            request.parkingName,
                                            request.shortName,
                                            request.founderName,
                                            request.logoUrl,
                                            request.websiteUrl,
                                            request.gstNumber,
                                            request.placeType,
                                            request.activeStatus,
                                            request.createdBy))
        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode": int(rows[0][1]),
            "response": rows[0][0]
        }
    except Exception as e:
        print("Exception as parkingOwnerMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

        
@router.put('')
async def putparkingOwnerMaster(request:schemas.PutParkingOwnerMaster,db: Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putParkingOwnerMaster]
                                            @parkingOwnerId=?,
                                            @userId=?,
                                            @parkingName=?,
                                            @shortName=?,
                                            @founderName=?,
                                            @logoUrl=?,
                                            @websiteUrl=?,
                                            @gstNumber=?,
                                            @placeType=?,
                                            @updatedBy=?
                                            """,
                                        (request.parkingOwnerId,
                                        request.userId,
                                        request.parkingName,
                                        request.shortName,
                                        request.founderName,
                                        request.logoUrl,
                                        request.websiteUrl,
                                        request.gstNumber,
                                        request.placeType,
                                        request.updatedBy))

        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode": int(rows[0][1]),
            "response": rows[0][0]
        }
    except Exception as e:
        print("Exception as putparkingOwnerMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.delete('')
async def deleteparkingownerMaster(parkingOwnerId:int,userId:int,activeStatus:str,db: Cursor=Depends(get_cursor)):
    try:
        result=await db.execute(f"""UPDATE parkingOwnerMaster SET activeStatus=? WHERE parkingOwnerId=? AND userId=?""",activeStatus,parkingOwnerId,userId)
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
        print("Exception as deleteparkingownerMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }