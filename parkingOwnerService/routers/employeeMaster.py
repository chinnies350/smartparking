from multiprocessing import connection
from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from fastapi import Response
from aioodbc.cursor import Cursor
from routers.eventsServer import publish
import schemas
# from routers.config import engine 
from routers.config import get_cursor
from task import passlot
import time
import json 
import datetime
from dotenv import load_dotenv
load_dotenv()
from typing import Optional
from fastapi import Query
import routers
import json,os
import asyncio


router = APIRouter(prefix="/employeeMaster",tags=['employeeMaster'])

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

async def getFloorDetailsBasedOnFloorId(floorId):
    try:
        
        response = await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/floorMaster?floorId={floorId}")
        response = json.loads(response.text)
        
        if response['statusCode'] == 1:
            return {
                        'floorName':response['response'][0]['floorName']
                    }
        return {}
    except Exception as e:
        print("Exception as getFloorDetailsBasedOnFloorId ",str(e))
        return {}

async def modifiedDataEmpTypeName(configId, dic):
    dic['empTypeName'] = await getConfigMasterNameByConfigId(configId)

async def modifiedDataEmpDesignationName(configId, dic):
    dic["empDesignationName"] = await getConfigMasterNameByConfigId(configId)

async def modifiedDatafloorNameAndFloorId(floorId, dic):
    res  = await getFloorDetailsBasedOnFloorId(floorId)
    dic.update(res)

async def getEmployeeDetailsBasedOnUserId(userId, floorId, blockId, branchId, parkingOwnerId, empDesignation, empType, db):
    dic = {}
    try:
        await db.execute("""SELECT CAST((SELECT em.employeeId,em.parkingOwnerId,em.branchId,em.DOJ,em.empType,em.empDesignation,em.shiftId,pom.parkingName,bm.branchName,(SELECT sm.shiftName FROM shiftMaster AS sm WHERE em.shiftId=sm.shiftId) AS shiftName,
                                bkm.blockId,bkm.blockName, em.floorId
                                FROM employeeMaster as em
                                INNER JOIN parkingOwnerMaster as pom ON pom.parkingOwnerId = em.parkingOwnerId
                                INNER JOIN branchMaster as bm ON bm.branchId = em.branchId
                                INNER JOIN blockMaster as bkm ON bkm.blockId = em.blockId
                                WHERE em.userId = ?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(userId))
        row = await db.fetchone()
        if row[0] != None:
            dic.update(json.loads(row[0])[0])

            await asyncio.gather(
                                    modifiedDataEmpTypeName(dic['empType'], dic), 
                                    modifiedDataEmpDesignationName(dic['empDesignation'], dic), 
                                    modifiedDatafloorNameAndFloorId(dic['floorId'], dic)
                                    )
            return {
                "response":dic,
                "statusCode":1
            }
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getEmployeeDetailsBasedOnUserId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

        # dic['empTypeName'] = await getConfigMasterNameByConfigId(dic['empType'])

async def getEmployeeDetailsBasedOnFloorId(userId, floorId, blockId, branchId, parkingOwnerId, empDesignation, empType, db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT em.userId,em.employeeId,em.parkingOwnerId,em.branchId,em.DOJ,em.empType,em.empDesignation,em.shiftId,pom.parkingName,bm.branchName,(SELECT sm.shiftName FROM shiftMaster AS sm WHERE em.shiftId=sm.shiftId) AS shiftName,
                                    bkm.blockId,bkm.blockName, em.floorId
                                    FROM employeeMaster as em
                                    INNER JOIN parkingOwnerMaster as pom ON pom.parkingOwnerId = em.parkingOwnerId
                                    INNER JOIN branchMaster as bm ON bm.branchId = em.branchId
                                    INNER JOIN blockMaster as bkm ON bkm.blockId = em.blockId
                                    WHERE em.floorId = ?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (floorId))
        row = await db.fetchone()

        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                                    modifiedDataEmpTypeName(dic['empType'], dic), 
                                    modifiedDataEmpDesignationName(dic['empDesignation'], dic), 
                                    modifiedDatafloorNameAndFloorId(dic['floorId'], dic)
                                    )
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
        print("Exception as getEmployeeDetailsBasedOnFloorId ",str(e))
        return {
            "response": str(e),
            "statusCode": 0
        }

async def getEmployeeDetailsBasedOnBlockId(userId, floorId, blockId, branchId, parkingOwnerId, empDesignation, empType, db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT em.userId,em.employeeId,em.parkingOwnerId,em.branchId,em.DOJ,em.empType,em.empDesignation,em.shiftId,pom.parkingName,bm.branchName,(SELECT sm.shiftName FROM shiftMaster AS sm WHERE em.shiftId=sm.shiftId) AS shiftName,
                                    bkm.blockId,bkm.blockName, em.floorId
                                    FROM employeeMaster as em
                                    INNER JOIN parkingOwnerMaster as pom ON pom.parkingOwnerId = em.parkingOwnerId
                                    INNER JOIN branchMaster as bm ON bm.branchId = em.branchId
                                    INNER JOIN blockMaster as bkm ON bkm.blockId = em.blockId
                                    WHERE em.blockId = ?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (blockId))
        row = await db.fetchone()

        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                                    modifiedDataEmpTypeName(dic['empType'], dic), 
                                    modifiedDataEmpDesignationName(dic['empDesignation'], dic), 
                                    modifiedDatafloorNameAndFloorId(dic['floorId'], dic)
                                    )
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
        print("Exception as getEmployeeDetailsBasedOnBlockId ",str(e))
        return {
            "response": str(e),
            "statusCode": 0
        }

async def getEmployeeDetailsBasedOnBranchId(userId, floorId, blockId, branchId, parkingOwnerId, empDesignation, empType, db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT em.userId,em.employeeId,em.parkingOwnerId,em.branchId,em.DOJ,em.empType,em.empDesignation,em.shiftId,pom.parkingName,bm.branchName,(SELECT sm.shiftName FROM shiftMaster AS sm WHERE em.shiftId=sm.shiftId) AS shiftName,
                                    bkm.blockId,bkm.blockName, em.floorId
                                    FROM employeeMaster as em
                                    INNER JOIN parkingOwnerMaster as pom ON pom.parkingOwnerId = em.parkingOwnerId
                                    INNER JOIN branchMaster as bm ON bm.branchId = em.branchId
                                    INNER JOIN blockMaster as bkm ON bkm.blockId = em.blockId
                                    WHERE em.branchId = ?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (branchId))
        row = await db.fetchone()

        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                                    modifiedDataEmpTypeName(dic['empType'], dic), 
                                    modifiedDataEmpDesignationName(dic['empDesignation'], dic), 
                                    modifiedDatafloorNameAndFloorId(dic['floorId'], dic)
                                    )
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
        print("Exception as getEmployeeDetailsBasedOnBranchId ",str(e))
        return {
            "response": str(e),
            "statusCode": 0
        }

async def getEmployeeDetailsBasedOnBranchIdEmpType(userId, floorId, blockId, branchId, parkingOwnerId, empDesignation, empType, db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT em.userId,em.employeeId,em.parkingOwnerId,em.branchId,em.DOJ,em.empType,em.empDesignation,em.shiftId,pom.parkingName,bm.branchName,(SELECT sm.shiftName FROM shiftMaster AS sm WHERE em.shiftId=sm.shiftId) AS shiftName,
                                    bkm.blockId,bkm.blockName, em.floorId
                                    FROM employeeMaster as em
                                    INNER JOIN parkingOwnerMaster as pom ON pom.parkingOwnerId = em.parkingOwnerId
                                    INNER JOIN branchMaster as bm ON bm.branchId = em.branchId
                                    INNER JOIN blockMaster as bkm ON bkm.blockId = em.blockId
                                    WHERE em.branchId = ? AND em.DOJ IS NOT NULL AND em.empType IS NOT NULL
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (branchId))
        row = await db.fetchone()

        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                                    modifiedDataEmpTypeName(dic['empType'], dic), 
                                    modifiedDataEmpDesignationName(dic['empDesignation'], dic), 
                                    modifiedDatafloorNameAndFloorId(dic['floorId'], dic)
                                    )
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
        print("Exception as getEmployeeDetailsBasedOnBranchIdEmpType ",str(e))
        return {
            "response": str(e),
            "statusCode": 0
        }

async def getEmployeeDetailsBasedOnParkingOwnerId(userId, floorId, blockId, branchId, parkingOwnerId, empDesignation, empType, db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((SELECT em.userId,em.employeeId,em.parkingOwnerId,em.branchId,em.DOJ,em.empType,em.empDesignation,em.shiftId,pom.parkingName,bm.branchName,(SELECT sm.shiftName FROM shiftMaster AS sm WHERE em.shiftId=sm.shiftId) AS shiftName,
                                    bkm.blockId,bkm.blockName, em.floorId
                                    FROM employeeMaster as em
                                    INNER JOIN parkingOwnerMaster as pom ON pom.parkingOwnerId = em.parkingOwnerId
                                    INNER JOIN branchMaster as bm ON bm.branchId = em.branchId
                                    INNER JOIN blockMaster as bkm ON bkm.blockId = em.blockId
                                    WHERE em.parkingOwnerId = ?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (parkingOwnerId))
        row = await db.fetchone()

        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                                    modifiedDataEmpTypeName(dic['empType'], dic), 
                                    modifiedDataEmpDesignationName(dic['empDesignation'], dic), 
                                    modifiedDatafloorNameAndFloorId(dic['floorId'], dic)
                                    )
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
        print("Exception as getEmployeeDetailsBasedOnParkingOwnerId ",str(e))
        return {
            "response": str(e),
            "statusCode": 0
        }

async def getEmployeeDetailsBasedOnEmpDesignationAndParkingOwnerId(userId, floorId, blockId, branchId, parkingOwnerId, empDesignation, empType, db):
    try:
        await db.execute(f"""
                            SELECT CAST((SELECT em.userId,em.employeeId,em.parkingOwnerId,em.branchId,em.DOJ,em.empType,em.empDesignation,em.shiftId,pom.parkingName,bm.branchName,(SELECT sm.shiftName FROM shiftMaster AS sm WHERE em.shiftId=sm.shiftId) AS shiftName,
                                    bkm.blockId,bkm.blockName, em.floorId
                                    FROM employeeMaster as em
                                    INNER JOIN parkingOwnerMaster as pom ON pom.parkingOwnerId = em.parkingOwnerId
                                    INNER JOIN branchMaster as bm ON bm.branchId = em.branchId
                                    INNER JOIN blockMaster as bkm ON bkm.blockId = em.blockId
                                    WHERE em.empDesignation = ? AND em.parkingOwnerId = ?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (empDesignation, parkingOwnerId))
        row = await db.fetchone()

        if row[0] != None:
            data = []
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                                    modifiedDataEmpTypeName(dic['empType'], dic), 
                                    modifiedDataEmpDesignationName(dic['empDesignation'], dic), 
                                    modifiedDatafloorNameAndFloorId(dic['floorId'], dic)
                                    )
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
        print("Exception as getEmployeeDetailsBasedOnEmpDesignationAndParkingOwnerId ",str(e))
        return {
            "response": str(e),
            "statusCode": 0
        }

async def getEmployeeDetailsBasedOnEmpDesignationAndBranchId(userId, floorId, blockId, branchId, parkingOwnerId, empDesignation, empType, db):
    try:
        await db.execute(f"""
                            SELECT CAST((SELECT em.userId,em.employeeId,em.parkingOwnerId,em.branchId,em.DOJ,em.empType,em.empDesignation,em.shiftId,pom.parkingName,bm.branchName,(SELECT sm.shiftName FROM shiftMaster AS sm WHERE em.shiftId=sm.shiftId) AS shiftName,
                                    bkm.blockId,bkm.blockName, em.floorId
                                    FROM employeeMaster as em
                                    INNER JOIN parkingOwnerMaster as pom ON pom.parkingOwnerId = em.parkingOwnerId
                                    INNER JOIN branchMaster as bm ON bm.branchId = em.branchId
                                    INNER JOIN blockMaster as bkm ON bkm.blockId = em.blockId
                                    WHERE em.empDesignation = ? AND em.branchId = ?
                                    FOR JSON PATH) AS VARCHAR(MAX))
                            """, (empDesignation, branchId))
        row = await db.fetchone()

        if row[0] != None:
            data = []
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await asyncio.gather(
                                    modifiedDataEmpTypeName(dic['empType'], dic), 
                                    modifiedDataEmpDesignationName(dic['empDesignation'], dic), 
                                    modifiedDatafloorNameAndFloorId(dic['floorId'], dic)
                                    )
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
        print("Exception as getEmployeeDetailsBasedOnEmpDesignationAndBranchId ",str(e))
        return {
            "response": str(e),
            "statusCode": 0
        }

employeeDic = {
    "userId=True, floorId=False, blockId=False, branchId=False, parkingOwnerId=False, empDesignation=False, empType=False":getEmployeeDetailsBasedOnUserId,
    "userId=False, floorId=True, blockId=False, branchId=False, parkingOwnerId=False, empDesignation=False, empType=False":getEmployeeDetailsBasedOnFloorId,
    "userId=False, floorId=False, blockId=True, branchId=False, parkingOwnerId=False, empDesignation=False, empType=False":getEmployeeDetailsBasedOnBlockId,
    "userId=False, floorId=False, blockId=False, branchId=True, parkingOwnerId=False, empDesignation=False, empType=False":getEmployeeDetailsBasedOnBranchId,
    "userId=False, floorId=False, blockId=False, branchId=True, parkingOwnerId=False, empDesignation=False, empType=True":getEmployeeDetailsBasedOnBranchIdEmpType,
    "userId=False, floorId=False, blockId=False, branchId=False, parkingOwnerId=True, empDesignation=False, empType=False":getEmployeeDetailsBasedOnParkingOwnerId,
    "userId=False, floorId=False, blockId=False, branchId=False, parkingOwnerId=True, empDesignation=True, empType=False":getEmployeeDetailsBasedOnEmpDesignationAndParkingOwnerId,
    "userId=False, floorId=False, blockId=False, branchId=True, parkingOwnerId=False, empDesignation=True, empType=False":getEmployeeDetailsBasedOnEmpDesignationAndBranchId
}


##################################################################################################################
@router.get('')
async def getEmployeeDetails(userId: Optional[int] = Query(None), floorId: Optional[int] = Query(None), blockId: Optional[int] = Query(None),branchId: Optional[int] = Query(None),parkingOwnerId: Optional[int] = Query(None), empDesignation: Optional[int] = Query(None), empType: Optional[int] = Query(None), db: Cursor = Depends(get_cursor)):
    try:
        st = f"userId={True if userId else False}, floorId={True if floorId else False}, blockId={True if blockId else False}, branchId={True if branchId else False}, parkingOwnerId={True if parkingOwnerId else False}, empDesignation={True if empDesignation else False}, empType={True if empType else False}"
        return await employeeDic[st](userId, floorId, blockId, branchId, parkingOwnerId, empDesignation, empType, db)
    except Exception as e:
        print("Exception as getEmployeeDetails ",str(e))
        return {
            "response": str(e),
            "statusCode": 0
        }
@router.post('')
async def postemployeeMaster(request:schemas.EmployeeMaster,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postEmployeeMaster]
                                        @parkingOwnerId=?,
                                        @branchId=?,
                                        @blockId=?,
                                        @floorId=?,
                                        @userId=?,
                                        @DOJ=?,
                                        @empType=?,
                                        @empDesignation=?,
                                        @shiftId=?,
                                        @createdBy=?""",
                                    (request.parkingOwnerId,
                                    request.branchId,
                                    request.blockId,
                                    request.floorId,
                                    request.userId,
                                    request.DOJ,
                                    request.empType,
                                    request.empDesignation,
                                    request.shiftId,
                                    request.createdBy))
                                        
        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as postemployeeMaster ",str(e))
        return {
            "response": str(e),
            "statusCode": 0
        }

@router.put('')
async def putemployeeMaster(request:schemas.PutemployeeMaster,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putemployeeMaster]
                                        @DOJ=?,
                                        @empType=?,
                                        @empDesignation=?,
                                        @updatedBy=?,
                                        @employeeId=?,
                                        @parkingOwnerId=?,
                                        @branchId=?,
                                        @blockId=?,
                                        @floorId=?,
                                        @userId=?,
                                        @shiftId=?""",
                                    (request.DOJ,
                                    request.empType,
                                    request.empDesignation,
                                    request.updatedBy,
                                    request.employeeId,
                                    request.parkingOwnerId,
                                    request.branchId,
                                    request.blockId,
                                    request.floorId,
                                    request.userId,
                                    request.shiftId
                                    ))
        row=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(row[0][1]),
            "response":row[0][0]
        }
    except Exception as e:
        print("Exception as putemployeeMaster ",str(e))
        return {
            "response": str(e),
            "statusCode": 0
        }
