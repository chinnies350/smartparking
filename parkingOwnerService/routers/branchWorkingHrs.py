from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from fastapi import Response
from aioodbc.cursor import Cursor
from routers.eventsServer import publish
import schemas
from typing import Optional
from fastapi import Query
# from routers.config import engine 
from routers.config import get_cursor
from task import passlot
import time
import json 
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/branchWorkingHrs",tags=['branchWorkingHrs'])

async def branchWorkingHrsDetailsBasedOnparkingOwnerId(parkingOwnerId,branchId,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bwv.* FROM branchWorkingHrsView AS bwv
                                WHERE parkingOwnerId = ?
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
        print("Exception as branchWorkingHrsDetailsBasedOnparkingOwnerId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def branchWorkingHrsDetailsBasedOnbranchId(parkingOwnerId,branchId,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bwv.* FROM branchWorkingHrsView AS bwv
                                WHERE branchId = ?
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
        print("Exception as branchWorkingHrsDetailsBasedOnbranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getbranchWorkingHrsDetails(parkingOwnerId,branchId,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT bwv.* FROM branchWorkingHrsView AS bwv
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
        print("Exception as getbranchWorkingHrsDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
    
branchWorkingHrsDict = {
    "parkingOwnerId=True,branchId=False":branchWorkingHrsDetailsBasedOnparkingOwnerId,
    "parkingOwnerId=False,branchId=True":branchWorkingHrsDetailsBasedOnbranchId,
    "parkingOwnerId=False,branchId=False":getbranchWorkingHrsDetails
}

@router.get('')
async def branchWorkingHrsGet(parkingOwnerId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"parkingOwnerId={True if parkingOwnerId else False},branchId={True if branchId else False}"
        return await branchWorkingHrsDict[st](parkingOwnerId,branchId,db)
    except Exception as e:
        print("Exception as branchWorkingHrsGet ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.post('')
async def postbranchWorkingHrs(request:schemas.BranchWorkingHrs,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postBranchWorkingHrs]
                                                @branchId =?,
                                                @parkingOwnerId =?,
                                                @workingDay =?,
                                                @fromTime =?,
                                                @toTime =?,
                                                @isHoliday =?,
                                                @createdBy =?""",
                                                (
                                                request.branchId,
                                                request.parkingOwnerId,
                                                request.workingDay,
                                                request.fromTime,
                                                request.toTime,
                                                request.isHoliday,
                                                request.createdBy))
        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as postbranchWorkingHrs ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.put('')
async def putbranchWorkingHrs(request:schemas.PutBranchWorkingHrs,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putBranchWorkingHrs]
                                                @uniqueId=?,
                                                @branchId =?,
                                                @parkingOwnerId =?,
                                                @workingDay =?,
                                                @fromTime =?,
                                                @toTime =?,
                                                @isHoliday =?,
                                                @updatedBy =?""",
                                                (
                                                request.uniqueId,
                                                request.branchId,
                                                request.parkingOwnerId,
                                                request.workingDay,
                                                request.fromTime,
                                                request.toTime,
                                                request.isHoliday,
                                                request.updatedBy))

        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as putbranchWorkingHrs ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

	
