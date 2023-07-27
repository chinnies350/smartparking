from fastapi.routing import  APIRouter
from fastapi import BackgroundTasks, Depends
from fastapi import Response
from aioodbc.cursor import Cursor
from routers.eventsServer import publish
import schemas
import routers
from typing import Optional
from fastapi import Query
# from routers.config import engine 
from routers.config import get_cursor
from task import passlot
import time
import json,os 
import asyncio
from task import postBlockName
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix="/blockMaster",tags=['blockMaster'])

async def getblockDetailsBasedOnblockId(blockId,activeStatus,parkingOwnerId,branchId,approvalStatus,db):
   
    try:
        await db.execute(f"""SELECT CAST((SELECT blv.* FROM  blockMasterView AS blv
                                WHERE blockId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(blockId))
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
        print("Exception as getblockDetailsBasedOnblockId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def blockDetailsBasedOnblockIdandactiveStatus(blockId,activeStatus,parkingOwnerId,branchId,approvalStatus, db):
    dic = {}
    try:
        await db.execute(f"""SELECT CAST((SELECT blv.* FROM  blockMasterView AS blv
                                WHERE blockId=? AND activeStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(blockId,activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            dic.update(json.loads(row[0])[0])
            return {
                "response":dic,
                "statusCode":1
            }

        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as blockDetailsBasedOnblockIdandactiveStatus",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getblockDetailsBasedOnparkingOwnerId(blockId,activeStatus,parkingOwnerId,branchId,approvalStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT blv.* FROM  blockMasterView AS blv
                                WHERE parkingOwnerId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(parkingOwnerId))
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
        print("Exception as getblockDetailsBasedOnparkingOwnerId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def blockDetailsBasedOnparkingOwnerIdandactiveStatus(blockId,activeStatus,parkingOwnerId,branchId,approvalStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT blv.* FROM  blockMasterView AS blv
                                WHERE parkingOwnerId=? AND activeStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(parkingOwnerId,activeStatus))
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
        print("Exception as blockDetailsBasedOnparkingOwnerIdandactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getblockDetailsBasedOnbranchId(blockId,activeStatus,parkingOwnerId,branchId,approvalStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT blv.* FROM  blockMasterView AS blv
                                WHERE branchId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(branchId))
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
        print("Exception as getblockDetailsBasedOnbranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def blockDetailsBasedOnbranchIdandactiveStatus(blockId,activeStatus,parkingOwnerId,branchId,approvalStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT blv.* FROM  blockMasterView AS blv
                                WHERE branchId=? AND activeStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(branchId,activeStatus))
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
        print("Exception as blockDetailsBasedOnbranchIdandactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def DetailsBasedOnbranchIdandactiveStatusandapprovalStatus(blockId,activeStatus,parkingOwnerId,branchId,approvalStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT blv.* FROM  blockMasterView AS blv
                                WHERE branchId=? AND activeStatus=? AND approvalStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(branchId,activeStatus,approvalStatus))
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
        print("Exception as DetailsBasedOnbranchIdandactiveStatusandapprovalStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def DetailsBasedOnbranchIdandparkingOwnerIdandapprovalStatus(blockId,activeStatus,parkingOwnerId,branchId,approvalStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT blv.* FROM  blockMasterView AS blv
                                WHERE branchId=? AND parkingOwnerId=? AND approvalStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(branchId,parkingOwnerId,approvalStatus))
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
        print("Exception as DetailsBasedOnbranchIdandparkingOwnerIdandapprovalStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getblockDetailsBasedOnactiveStatus(blockId,activeStatus,parkingOwnerId,branchId,approvalStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT blv.* FROM  blockMasterView AS blv
                                WHERE activeStatus=? 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus))
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
        print("Exception as getblockDetailsBasedOnactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getblockDetailsBasedOnapprovalStatus(blockId,activeStatus,parkingOwnerId,branchId,approvalStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT blv.* FROM  blockMasterView AS blv
                                WHERE approvalStatus=? 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(approvalStatus))
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
        print("Exception as getblockDetailsBasedOnapprovalStatus",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getblockDetails(blockId,activeStatus,parkingOwnerId,branchId,approvalStatus, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT blv.* FROM  blockMasterView AS blv 
                                FOR JSON PATH) AS VARCHAR(MAX))""")
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
        print("Exception as getblockDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

blockDict = {
    "blockId=True,activeStatus=False,parkingOwnerId=False,branchId=False,approvalStatus=False":getblockDetailsBasedOnblockId,
    "blockId=True,activeStatus=True,parkingOwnerId=False,branchId=False,approvalStatus=False":blockDetailsBasedOnblockIdandactiveStatus,
    "blockId=False,activeStatus=False,parkingOwnerId=True,branchId=False,approvalStatus=False":getblockDetailsBasedOnparkingOwnerId,
    "blockId=False,activeStatus=True,parkingOwnerId=True,branchId=False,approvalStatus=False":blockDetailsBasedOnparkingOwnerIdandactiveStatus,
    "blockId=False,activeStatus=False,parkingOwnerId=False,branchId=True,approvalStatus=False":getblockDetailsBasedOnbranchId,
    "blockId=False,activeStatus=True,parkingOwnerId=False,branchId=True,approvalStatus=False":blockDetailsBasedOnbranchIdandactiveStatus,
    "blockId=False,activeStatus=True,parkingOwnerId=False,branchId=True,approvalStatus=True":DetailsBasedOnbranchIdandactiveStatusandapprovalStatus,
    "blockId=False,activeStatus=False,parkingOwnerId=True,branchId=True,approvalStatus=True":DetailsBasedOnbranchIdandparkingOwnerIdandapprovalStatus,
    "blockId=False,activeStatus=True,parkingOwnerId=False,branchId=False,approvalStatus=False":getblockDetailsBasedOnactiveStatus,
    "blockId=False,activeStatus=False,parkingOwnerId=False,branchId=False,approvalStatus=True":getblockDetailsBasedOnapprovalStatus,
    "blockId=False,activeStatus=False,parkingOwnerId=False,branchId=False,approvalStatus=False":getblockDetails
}

##################################################################################################################
@router.get('')
async def blockMasterGet(blockId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),parkingOwnerId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),approvalStatus:Optional[str]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"blockId={True if blockId else False},activeStatus={True if activeStatus else False},parkingOwnerId={True if parkingOwnerId else False},branchId={True if branchId else False},approvalStatus={True if approvalStatus else False}"
        return await blockDict[st](blockId,activeStatus,parkingOwnerId,branchId,approvalStatus, db)
    except Exception as e:
        print("Exception as blockMasterGet ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
@router.post('')
async def postblockMaster(request:schemas.BlockMaster,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postBlockMaster]
                                        @parkingOwnerId=?,
                                        @branchId=?,
                                        @blockName=?,
                                        @activeStatus=?,
                                        @approvalStatus=?,
                                        @createdBy=?
                                        """,
                                        (request.parkingOwnerId,
                                        request.branchId,
                                        request.blockName,
                                        request.activeStatus,
                                        request.approvalStatus,
                                        request.createdBy)
                                        )
        rows=await db.fetchone()
        await db.commit()
        if int(rows[1])==1:
            postBlockName.delay(int(rows[2]),request.blockName)
            return{
                "statusCode":int(rows[1]),
                "response":rows[0]
            }
        return{
                "statusCode":int(rows[1]),
                "response":rows[0]
            }
    except Exception as e:
        print("Exception as postblockMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.put('')
async def putblockMaster(request:schemas.PutBlockMaster,db:Cursor=Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putBlockMaster]
                                                    @blockId=?,
                                                    @parkingOwnerId=?,
                                                    @branchId=?,
                                                    @blockName=?,
                                                    @approvalStatus=?,
                                                    @updatedBy=?
                                                    """,
                                                    (
                                                    request.blockId,
                                                    request.parkingOwnerId,
                                                    request.branchId,
                                                    request.blockName,
                                                    request.approvalStatus,
                                                    request.updatedBy))
        rows=await db.fetchone()
        await db.commit()
        if int(rows[1])==1:
            postBlockName.delay(request.branchId,request.blockName)
            return{
                "statusCode":int(rows[1]),
                "response":rows[0]
            }
        return{
                "statusCode":int(rows[1]),
                "response":rows[0]
            }
    except Exception as e:
        print("Exception as putblockMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.delete('')
async def deleteblockMaster(blockId:int,activeStatus:str,db:Cursor=Depends(get_cursor)):
    try:
        if activeStatus == 'A':
            result = await db.execute(f"""
                    DECLARE @branchId INT, 
                    @blockName nvarchar(50),
                    @blockId INT = ?
                    SELECT @branchId=branchId, @blockName = blockName FROM blockMaster
                    WHERE blockId= @blockId

                    SELECT * FROM blockMaster 
                    WHERE branchId = @branchId AND blockName = @blockName AND activeStatus = 'A' AND blockId != @blockId
            """, (blockId))
            row = result.fetchone()
            if row != None:
                return {
                    'statusCode':0,
                    "response": 'Data Already Exists'
                }
        result=await db.execute(f"""UPDATE blockMaster SET activeStatus=? WHERE blockId=?""",(activeStatus,blockId))
        await db.commit()
        if result.rowcount>=1:
            if activeStatus=='D':
                return{
                    "statusCode":1,
                    "response":"Deactivated Successfully"
                }
            else:
                return{
                    "statusCode":1,
                    "response":"Activated Successfully"
                }
        else:
            return{
                "statusCode":0,
                "response":"Data Not Deleted"
            }
    except Exception as e:
        print("Exception as deleteblockMaster ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

