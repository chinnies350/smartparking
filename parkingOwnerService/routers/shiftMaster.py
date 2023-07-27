from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from fastapi import Response
from aioodbc.cursor import Cursor
from routers.eventsServer import publish
import schemas
from typing import Optional
from fastapi import Query
# from routers.config import engine 
from routers.config import get_cursor,redis_client
from task import passlot
import time
import json 
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/shiftMaster",tags=['shiftMaster'])

# async def send_event_to_event_server(queName:str, message:dict):
#     await publish(queName,message.dict())

async def shiftDetailsBasedOnshiftId(shiftId,activeStatus,parkingOwnerId,branchId, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT smv.* FROM shiftMasterView AS smv
                                WHERE smv.shiftId = ? AND smv.activeStatus =?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (shiftId,activeStatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as shiftDetailsBasedOnshiftId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def shiftDetailsBasedOnparkingOwnerId(shiftId,activeStatus,parkingOwnerId,branchId, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT smv.* FROM shiftMasterView AS smv
                                WHERE smv.parkingOwnerId = ? 
                                FOR JSON PATH) AS VARCHAR(MAX))""", (parkingOwnerId))
        row = await db.fetchone()
        if row[0] != None:          
            data=(json.loads(row[0]))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as shiftDetailsBasedOnparkingOwnerId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def shiftDetailsBasedOnbranchId(shiftId,activeStatus,parkingOwnerId,branchId, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT smv.* FROM shiftMasterView AS smv
                                WHERE smv.branchId = ? 
                                FOR JSON PATH) AS VARCHAR(MAX))""", (branchId))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as shiftDetailsBasedOnbranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def shiftDetailsBasedOnbranchIdActivestatus(shiftId,activeStatus,parkingOwnerId,branchId, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT smv.* FROM shiftMasterView AS smv
                                WHERE smv.branchId = ? AND smv.activeStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (branchId,activeStatus))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as shiftDetailsBasedOnbranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def GetshiftDetails(shiftId,activeStatus,parkingOwnerId,branchId, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT smv.* FROM shiftMasterView AS smv
                                FOR JSON PATH) AS VARCHAR(MAX))""")
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            return {
            "response":data,
            "statusCode":1
        }                
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as GetshiftDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
    


shiftDict = {
    "shiftId=True,activeStatus=True,parkingOwnerId=False,branchId=False":shiftDetailsBasedOnshiftId,
    "shiftId=False,activeStatus=False,parkingOwnerId=True,branchId=False":shiftDetailsBasedOnparkingOwnerId,
    "shiftId=False,activeStatus=False,parkingOwnerId=False,branchId=True":shiftDetailsBasedOnbranchId,
    "shiftId=False,activeStatus=True,parkingOwnerId=False,branchId=True":shiftDetailsBasedOnbranchIdActivestatus,
    "shiftId=False,activeStatus=False,parkingOwnerId=False,branchId=False":GetshiftDetails
}

@router.get('')
async def shiftMasterGet(shiftId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),parkingOwnerId:Optional[int]=Query(None),branchId:Optional[int]=Query(None), db:Cursor = Depends(get_cursor)):
    try:
        st = f"shiftId={True if shiftId else False},activeStatus={True if activeStatus else False},parkingOwnerId={True if parkingOwnerId else False},branchId={True if branchId else False}"
        return await shiftDict[st](shiftId,activeStatus,parkingOwnerId,branchId, db)
    except Exception as e:
        print("Exception as shiftMasterGet ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.post('')
async def postshiftMaster(request:schemas.shiftMaster,db: Cursor=Depends (get_cursor)):
    try:
        shiftConfigName = redis_client.hget('configMaster', request.shiftName)
        shiftConfigName=shiftConfigName.decode("utf-8") if shiftConfigName else None

        await db.execute(f"""EXEC [dbo].[postshiftMaster]
                                        @parkingOwnerId=?,
                                        @branchId=?,
                                        @shiftName=?,
                                        @shiftConfigName=?,
                                        @startTime=?,
                                        @endTime=?,
                                        @breakStartTime=?,
                                        @breakEndTime=?,
                                        @gracePeriod=?,
                                        @activeStatus=?,
                                        @createdBy=?""",
                                        (request.parkingOwnerId,
                                        request.branchId,
                                        request.shiftName,
                                        shiftConfigName,
                                        request.startTime,
                                        request.endTime,
                                        request.breakStartTime,
                                        request.breakEndTime,
                                        request.gracePeriod,
                                        request.activeStatus,
                                        request.createdBy))

        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response": rows[0][0]
        }
    except Exception as e:
        print("Exception as postshiftMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.put('')
async def putshiftMaster(request:schemas.putshiftMaster,db:Cursor=Depends(get_cursor)):
    try:
        shiftConfigName = redis_client.hget('configMaster', request.shiftName)
        shiftConfigName=shiftConfigName.decode("utf-8") if shiftConfigName else None

        await db.execute(f"""EXEC [dbo].[putshiftMaster] 
                                        @shiftName=?,
                                        @shiftConfigName=?,
                                        @startTime=?,
                                        @endTime=?,
                                        @breakStartTime=?,
                                        @breakEndTime=?,
                                        @gracePeriod=?,
                                        @activeStatus=?,
                                        @updatedBy=?,
                                        @shiftId=?,
                                        @parkingOwnerId=?,
                                        @branchId=?""",
                                        (request.shiftName,
                                        shiftConfigName,
                                        request.startTime,
                                        request.endTime,
                                        request.breakStartTime,
                                        request.breakEndTime,
                                        request.gracePeriod,
                                        request.activeStatus,
                                        request.updatedBy,
                                        request.shiftId,
                                        request.parkingOwnerId,
                                        request.branchId))

        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as putshiftMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.delete('')
async def deleteshiftMaster(shiftId:int,activeStatus:str,db:Cursor=Depends(get_cursor)):
    try:
        result=await db.execute(f"""UPDATE shiftMaster SET activeStatus=? WHERE shiftId=?""",(activeStatus,shiftId))
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
        print("Exception as deleteshiftMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

