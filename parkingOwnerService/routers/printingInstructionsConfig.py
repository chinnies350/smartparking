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
from joblib import Parallel, delayed 
from dotenv import load_dotenv
load_dotenv()

def callFunction(i):
    return i.dict()

router = APIRouter(prefix="/printingInstructionsConfig",tags=['printingInstructionsConfig'])
router1 = APIRouter(prefix="/printingInstructionsConfig1", tags=['printingInstructionsConfig'])

async def printingInstructionsDetailsBasedOnuniqueId(uniqueId,parkingOwnerId,branchId,instructionType,activeStatus,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT piv.* FROM printingInstructionsConfigView AS piv
                                WHERE uniqueId = ? 
                                FOR JSON PATH) AS VARCHAR(MAX))""", (uniqueId))
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
        print("Exception as printingInstructionsDetailsBasedOnuniqueId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def printingInstructionsDetailsBasedOnparkingOwnerId(uniqueId,parkingOwnerId,branchId,instructionType,activeStatus,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT piv.* FROM printingInstructionsConfigView AS piv
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
        print("Exception as printingInstructionsDetailsBasedOnparkingOwnerId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def printingInstructionsDetailsBasedOnbranchId(uniqueId,parkingOwnerId,branchId,instructionType,activeStatus,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT piv.* FROM printingInstructionsConfigView AS piv
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
        print("Exception as printingInstructionsDetailsBasedOnbranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def printingInstructionsDetailsBasedOnbranchIdInstructionType(uniqueId,parkingOwnerId,branchId,instructionType,activeStatus,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT piv.* FROM printingInstructionsConfigView AS piv
                                WHERE piv.branchId = ? AND piv.instructionType=?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (branchId,instructionType))
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
        print("Exception as printingInstructionsDetailsBasedOnbranchIdInstructionType ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def DetailsBasedOnbranchIdInstructionTypeActivestatus(uniqueId,parkingOwnerId,branchId,instructionType,activeStatus,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT piv.* FROM printingInstructionsConfigView AS piv
                                WHERE piv.branchId = ? AND piv.instructionType=? AND piv.activeStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""", (branchId,instructionType,activeStatus))
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
        print("Exception as DetailsBasedOnbranchIdInstructionTypeActivestatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def GetprintingInstructionsDetails(uniqueId,parkingOwnerId,branchId,instructionType,activeStatus,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT piv.* FROM printingInstructionsConfigView AS piv
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
        print("Exception as GetprintingInstructionsDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }



printingInstructionsConfigDict = {
    "uniqueId=True,parkingOwnerId=False,branchId=False,instructionType=False,activeStatus=False":printingInstructionsDetailsBasedOnuniqueId,
    "uniqueId=False,parkingOwnerId=True,branchId=False,instructionType=False,activeStatus=False":printingInstructionsDetailsBasedOnparkingOwnerId,
    "uniqueId=False,parkingOwnerId=False,branchId=True,instructionType=False,activeStatus=False":printingInstructionsDetailsBasedOnbranchId,
    "uniqueId=False,parkingOwnerId=False,branchId=True,instructionType=True,activeStatus=False":printingInstructionsDetailsBasedOnbranchIdInstructionType,
    "uniqueId=False,parkingOwnerId=False,branchId=True,instructionType=True,activeStatus=True":DetailsBasedOnbranchIdInstructionTypeActivestatus,
    "uniqueId=False,parkingOwnerId=False,branchId=False,instructionType=False,activeStatus=False":GetprintingInstructionsDetails
}


@router.get('')
async def printingInstructionsConfigGet(uniqueId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),instructionType:Optional[str]=Query(None),activeStatus:Optional[str]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"uniqueId={True if uniqueId else False},parkingOwnerId={True if parkingOwnerId else False},branchId={True if branchId else False},instructionType={True if instructionType else False},activeStatus={True if activeStatus else False}"
        return await printingInstructionsConfigDict[st](uniqueId,parkingOwnerId,branchId,instructionType,activeStatus, db)
    except Exception as e:
        print("Exception as printingInstructionsConfigGet ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
@router.post('')
async def postprintingInstructionsConfig(request:schemas.PrintingInstructionsConfig,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postPrintingInstructionsConfig]
                                                    @parkingOwnerId =?,
                                                    @branchId =?,
                                                    @instructionType =?,
                                                    @instructions=?,
                                                    @createdBy =?
                                                    
                                                    """,
                                                (request.parkingOwnerId,
                                                request.branchId,
                                                request.instructionType,
                                                request.instructions,
                                                request.createdBy
                                                ))
        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as postprintingInstructionsConfig ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.put('')
async def putprintingInstructionsConfig(request:schemas.PutPrintingInstructionsConfig,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putPrintingInstructionsConfig]
                                                    @parkingOwnerId =?,
                                                    @branchId =?,
                                                    @instructionType =?,
                                                    @instructions=?,
                                                    @updatedBy =?,
                                                    @uniqueId=?
                                                    """,
                                                (
                                                request.parkingOwnerId,
                                                request.branchId,
                                                request.instructionType,
                                                request.instructions,
                                                request.updatedBy,
                                                request.uniqueId
                                                ))
        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as putprintingInstructionsConfig ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.delete('')
async def deletePrintingInstructionsConfig(uniqueId:int,activeStatus:str,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE printingInstructionsConfig SET activeStatus=? WHERE uniqueId=?",activeStatus,uniqueId)
        await db.commit()
        if result.rowcount>=1:
            if activeStatus=='D':
                return {
                         "statusCode": 1,
                         "response": "Deactivated successfully"}
            else:
                return {"statusCode": 1,
                        "response": "Activated successfully"}
        else:
            return { "statusCode": 0,
                    "response": "Data Not Found"}

    except Exception as e:
        print("Exception as deletePrintingInstructionsConfig ",str(e))
        return{"stausCode":0, "response":"Server Error"}


@router1.post('')
async def postprintingInstructionsConfig1(request:schemas.PrintingInstructionsConfig1,db:Cursor=Depends(get_cursor)):
    try:
        r = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.instructionsDetails)
        await db.execute(f"""EXEC [dbo].[postPrintingInstructionsConfig1]
                                                @parkingOwnerId =?,
                                                @branchId =?,
                                                @instructionType =?,
                                                @PrintingInstructionsDetailsJson=?,
                                                @createdBy =?
                                                
                                                """,
                                            (request.parkingOwnerId,
                                            request.branchId,
                                            request.instructionType,
                                            json.dumps(r,indent=4, sort_keys=True, default=str),
                                            request.createdBy
                                            )
                                            )
        rows=await db.fetchall()
        await db.commit()
        return{
            "statusCode":int(rows[0][1]),
            "response":rows[0][0]
        }
    except Exception as e:
        print("Exception as postprintingInstructionsConfig1 ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
