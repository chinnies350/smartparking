from fastapi import Query
from fastapi.routing import APIRouter
from typing import Optional,List
from routers.config import get_cursor
from fastapi import Depends
from aioodbc.cursor import Cursor
import json,os
import routers
from dotenv import load_dotenv
load_dotenv()
import ast

router = APIRouter(prefix='/parkingLotLine',tags=['parkingLotLine'])

async def parkingLotLineDetailsBasedOnbranchId(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    data =[]
    try:
        await db.execute(f"""SELECT CAST((SELECT COUNT(parkingSlotId) AS COUNT
                                        FROM parkingLotLine as pll
                                        INNER JOIN parkingSlot as ps ON ps.parkingLotLineId = pll.parkingLotLineId
                                        WHERE ps.slotState='N' AND pll.branchId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(branchId))
        row = await db.fetchone()
        if row[0] != None:           
            data=(json.loads(row[0]))
            return {
            "response":data,
            "statusCode":1
            }
        else:
            {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as parkingLotLineDetailsBasedOnbranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def parkingLotLineDetailsbasedOnfloorId(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    data =[]
    try:
        await db.execute(f"""SELECT CAST((SELECT COUNT(ps.parkingSlotId) AS totalSlot
                                    FROM parkingLotLine as pll 
                                    INNER JOIN parkingSlot as ps 
                                    ON pll.parkingLotLineId = ps.parkingLotLineId 
                                    WHERE pll.floorId = ? 
                                    AND ps.activeStatus IN {tuple(i['configId'] for i in ast.literal_eval(activeStatus[0]))+tuple('0')}
                                    FOR JSON Path) AS varchar(max))""",floorId)
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
    except Exception as e:
        print("Exception as parkingLotLineDetailsbasedOnfloorId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def parkingLotLineDetailsbasedOnblockId(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    data =[]
    try:
        await db.execute(f"""SELECT CAST((SELECT COUNT(ps.parkingSlotId) AS totalSlot
                            FROM parkingLotLine as pll 
                            INNER JOIN parkingSlot as ps 
                            ON pll.parkingLotLineId = ps.parkingLotLineId 
                            WHERE pll.blockId = ? 
                            AND ps.activeStatus IN {tuple(i['configId'] for i in ast.literal_eval(activeStatus[0]))+tuple('0')}
                            FOR JSON Path) AS varchar(max))""",blockId)
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
    except Exception as e:
        print("Exception as parkingLotLineDetailsbasedOnblockId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def parkingLotLineDetailsbasedOnparkingOwnerId(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    data =[]
    try:        
        await db.execute(f"""SELECT CAST((SELECT COUNT(ps.parkingSlotId) AS totalSlot
                            FROM parkingLotLine as pll 
                            INNER JOIN parkingSlot as ps 
                            ON pll.parkingLotLineId = ps.parkingLotLineId 
                            WHERE pll.parkingOwnerId = ? 
                            AND ps.activeStatus IN {tuple(i['configId'] for i in ast.literal_eval(activeStatus[0]))+tuple('0')}
                            FOR JSON Path) AS varchar(max))""",parkingOwnerId)
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
    except Exception as e:
        print("Exception as parkingLotLineDetailsbasedOnparkingOwnerId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def parkingLotLineDetails(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    data =[]
    try:        
        await db.execute(f"""SELECT CAST((SELECT COUNT(ps.parkingSlotId) AS totalSlot, pll.branchId
                    FROM parkingLotLine as pll 
                    INNER JOIN parkingSlot as ps 
                    ON pll.parkingLotLineId = ps.parkingLotLineId 
                    WHERE ps.activeStatus IN {tuple(i['configId'] for i in ast.literal_eval(activeStatus[0]))+tuple('0')}
                    FOR JSON Path) AS varchar(max))""")
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
    except Exception as e:
        print("Exception as parkingLotLineDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def parkingLotLineDetailsBasedOnCheckBranchIds(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    try:
        
        data=[]
        await db.execute(f"""SELECT CAST((SELECT pll.branchId 
                                     FROM parkingLotLine AS pll
                                     INNER JOIN parkingSlot AS ps
                                     ON pll.parkingLotLineId=ps.parkingLotLineId
                                     WHERE ps.parkingSlotId NOT IN {(tuple(j['slotId'] for i in ast.literal_eval(checkBranchSlotIds[0]) for j in i['us'])+tuple('0'))} 
                                     AND pll.typeOfVehicle={typeOfVehicle}
                                     AND ps.activeStatus IN {tuple(i['configId'] for i in ast.literal_eval(activeStatus[0]))+tuple('0')} 
                                     AND pll.activeStatus='A'
                                            FOR JSON Path) AS  varchar(max))""")
      
        row = await db.fetchone()
        
        if row[0] != None:
            for i in json.loads(row[0]):
                data.append(i['branchId'])
            
            return {
                "statusCode":1,
                "response": data
            
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as parkingLotLineDetailsBasedOnCheckBranchIds ",str(e))
        return{"statusCode":0,"response":"Server Error"}

async def parkingLotLineDetailsBasedOnTypeofVehicle(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    try:
        
        data=[]
        await db.execute(f"""SELECT CAST((SELECT pll.branchId 
                                     FROM parkingLotLine AS pll
                                     WHERE pll.typeOfVehicle={typeOfVehicle}
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                data.append(i['branchId'])
            
            return {
                "statusCode":1,
                "response": data
            
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as parkingLotLineDetailsBasedOnTypeofVehicle ",str(e))
        return{"statusCode":0,"response":"Server Error"}

async def parkingLotLineDetailsBasedOnActiveBranchIdTypeOfVehicle(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    try:
        
        print("lllllllllllll",branchId,tuple(i['configId'] for i in ast.literal_eval(activeStatus[0]))+tuple('0'),typeOfVehicle,(tuple(j['slotId'] for i in ast.literal_eval(checkBranchSlotIds[0]) for j in i['us'])+tuple('0')))
        await db.execute(f"""SELECT CAST((
                                                    SELECT COUNT(parkingSlotId) AS parkingSlotIdCount
                                                    FROM parkingLotLine as pll 
                                                    INNER JOIN parkingSlot as ps 
                                                    ON pll.parkingLotLineId = ps.parkingLotLineId 
                                                    WHERE pll.branchId = ? 
                                                    AND ps.activeStatus IN {tuple(i['configId'] for i in ast.literal_eval(activeStatus[0]))+tuple('0')} 
                                                    AND pll.activeStatus='A'
                                                    AND ps.parkingSlotId NOT IN {(tuple(j['slotId'] for i in ast.literal_eval(checkBranchSlotIds[0]) for j in i['us'])+tuple('0'))} 
                                                    AND pll.typeOfVehicle={typeOfVehicle}
                                                    FOR JSON Path) AS varchar(max))
                                                
                                            """,branchId)
        row = await db.fetchone()
        print("row",row)
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as parkingLotLineDetailsBasedOnActiveBranchIdTypeOfVehicle ",str(e))
        return{"statusCode":0,"response":"Server Error"}

async def parkingLotLineDetailsBasedOnActiveBranchIdType(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    try:
        data=[]                
        await db.execute(f"""SELECT CAST((SELECT COUNT(parkingSlotId) AS slotAvailable
                                            FROM parkingLotLine as pll 
                                            INNER JOIN parkingSlot as ps 
                                            ON pll.parkingLotLineId = ps.parkingLotLineId 
                                            WHERE ps.activeStatus IN {tuple(i['configId'] for i in ast.literal_eval(activeStatus[0]))+tuple('0')} 
                                            AND pll.activeStatus='A'
                                            AND ps.parkingSlotId NOT IN {(tuple(j['slotId'] for i in ast.literal_eval(checkBranchSlotIds[0]) for j in i['us'])+tuple('0'))} 
                                            FOR JSON Path) AS varchar(max))""")
        row = await db.fetchone()
        print('row111111111111',row)
        if row[0] != None:
            data=(json.loads(row[0]))
            return {
                "statusCode":1,
                "response": data
            
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as parkingLotLineDetailsBasedOnActiveBranchIdType ",str(e))
        return{"statusCode":0,"response":"Server Error"}

async def parkingLotLineDetailsBasedOnActiveBranchId(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    try:
                
        await db.execute(f"""SELECT CAST((SELECT COUNT(ps.parkingSlotId) AS totalSlot
                                            FROM parkingLotLine as pll 
                                            INNER JOIN parkingSlot as ps 
                                            ON pll.parkingLotLineId = ps.parkingLotLineId 
                                            WHERE pll.branchId = ? AND pll.activeStatus='A'
                                            AND ps.activeStatus IN {tuple(i['configId'] for i in ast.literal_eval(activeStatus[0]))+tuple('0')}
                                            FOR JSON Path) AS varchar(max))""",branchId)
        row = await db.fetchone()
        
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as parkingLotLineDetailsBasedOnActiveBranchId ",str(e))
        return{"statusCode":0,"response":"Server Error"}

async def parkingLotLineDetailsBasedOnSlotExist(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    try:
        
        
        await db.execute(f"""SELECT CAST((SELECT (CASE WHEN EXISTS(SELECT * FROM parkingLotLine as pll WHERE pll.branchId = ?)
									THEN 'Y'
									ELSE	
										'N'
									END) as slotExist
                                            FOR JSON Path) AS varchar(max))""",slotExist)
        row = await db.fetchone()
        
        if row[0] != None:
            return {
                "statusCode":1,
                "response": json.loads(row[0])
            
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as parkingLotLineDetailsBasedOnSlotExist ",str(e))
        return{"statusCode":0,"response":"Server Error"}

async def AllparkingLotLineDetails(branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds, activeStatus, slotExist,typeOfVehicle, db):
    try:
        data=[]
        await db.execute(f"""SELECT CAST((SELECT pll.branchId 
                                     FROM parkingLotLine AS pll
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                data.append(i['branchId'])
            
            return {
                "statusCode":1,
                "response": data
            
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as AllparkingLotLineDetails ",str(e))
        return{"statusCode":0,"response":"Server Error"}

parkingLotLineDict = {
    "branchId=True, floorId=False, blockId=False, parkingOwnerId=False, checkBranchSlotIds=False, activeStatus=False, slotExist=False, typeOfVehicle=False":parkingLotLineDetailsBasedOnbranchId,
    "branchId=False, floorId=True, blockId=False, parkingOwnerId=False, checkBranchSlotIds=False, activeStatus=True, slotExist=False, typeOfVehicle=False":parkingLotLineDetailsbasedOnfloorId,
    "branchId=False, floorId=False, blockId=True, parkingOwnerId=False, checkBranchSlotIds=False, activeStatus=True, slotExist=False, typeOfVehicle=False":parkingLotLineDetailsbasedOnblockId,
    "branchId=False, floorId=False, blockId=False, parkingOwnerId=True, checkBranchSlotIds=False, activeStatus=True, slotExist=False, typeOfVehicle=False":parkingLotLineDetailsbasedOnparkingOwnerId,
    "branchId=False, floorId=False, blockId=False, parkingOwnerId=False, checkBranchSlotIds=False, activeStatus=True, slotExist=False, typeOfVehicle=False":parkingLotLineDetails,
    "branchId=False, floorId=False, blockId=False, parkingOwnerId=False, checkBranchSlotIds=True, activeStatus=True, slotExist=False, typeOfVehicle=True":parkingLotLineDetailsBasedOnCheckBranchIds,
    "branchId=False, floorId=False, blockId=False, parkingOwnerId=False, checkBranchSlotIds=False, activeStatus=False, slotExist=False, typeOfVehicle=True":parkingLotLineDetailsBasedOnTypeofVehicle,
    "branchId=True, floorId=False, blockId=False, parkingOwnerId=False, checkBranchSlotIds=True, activeStatus=True, slotExist=False, typeOfVehicle=True":parkingLotLineDetailsBasedOnActiveBranchIdTypeOfVehicle,
    "branchId=True, floorId=False, blockId=False, parkingOwnerId=False, checkBranchSlotIds=False, activeStatus=True, slotExist=False, typeOfVehicle=False":parkingLotLineDetailsBasedOnActiveBranchId,
    "branchId=False, floorId=False, blockId=False, parkingOwnerId=False, checkBranchSlotIds=False, activeStatus=False, slotExist=True, typeOfVehicle=False":parkingLotLineDetailsBasedOnSlotExist,
    "branchId=False, floorId=False, blockId=False, parkingOwnerId=False, checkBranchSlotIds=True, activeStatus=True, slotExist=False, typeOfVehicle=False":parkingLotLineDetailsBasedOnActiveBranchIdType,
    "branchId=False, floorId=False, blockId=False, parkingOwnerId=False, checkBranchSlotIds=False, activeStatus=False, slotExist=False, typeOfVehicle=False":AllparkingLotLineDetails,
}

##################################################################################################################
@router.get('')
async def parkingLotLineGet(branchId:Optional[int]=Query(None),floorId:Optional[int]=Query(None),blockId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None),checkBranchSlotIds:Optional[List]=Query(None),activeStatus:Optional[List]=Query(None),slotExist:Optional[int]=Query(None),typeOfVehicle:Optional[int]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"branchId={True if branchId else False}, floorId={True if floorId else False}, blockId={True if blockId else False}, parkingOwnerId={True if parkingOwnerId else False}, checkBranchSlotIds={True if checkBranchSlotIds else False}, activeStatus={True if activeStatus else False}, slotExist={True if slotExist else False}, typeOfVehicle={True if typeOfVehicle else False}"
        return await parkingLotLineDict[st](branchId,floorId,blockId,parkingOwnerId,checkBranchSlotIds,activeStatus,slotExist,typeOfVehicle, db)
    except Exception as e:
        print("Exception as parkingLotLineGet",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }