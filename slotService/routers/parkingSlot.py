from fastapi import Query
from fastapi.routing import APIRouter
from typing import Optional,List
from routers.config import get_cursor,redis_client
from fastapi import Depends
from aioodbc.cursor import Cursor
import json,os
import routers
import schemas
from joblib import Parallel, delayed
import asyncio
import ast
from datetime import datetime,time,date

from dotenv import load_dotenv
load_dotenv()



def callFunction(i):
    i=i.dict()
    activeDetails=redis_client.hget('configMaster', i['activeStatus'])
    chargePinConfigMasterDetails=redis_client.hget('chargePinConfigMaster', i['chargePinType']) if i['chargePinType']!=0 else None
    
    i['chargePinConfig'],i['chargePinImageUrl'] = None, None
   
    if chargePinConfigMasterDetails!=None:
        i['chargePinConfig'],i['chargePinImageUrl']=tuple(json.loads(chargePinConfigMasterDetails.decode("utf-8")).values())
    
    i['activeStatusName']=activeDetails.decode("utf-8") if activeDetails else None
    return i

parkingSlotRouter=APIRouter(prefix="/parkingSlot",tags=['parkingSlot'])



async def parkingSlotDetailsBasedOnBranchIdAndActiveStatus(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        await db.execute(f"""SELECT CAST((select * from parkingSlotView where branchId=? and activeStatus=?
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
        print("Exception as getblockDetailsBasedOnblockId",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        
async def getparkingslotdetailsbasedonparkingSlotId(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:            
        await db.execute(f"""
                            SELECT CAST((SELECT * 
                            from parkingSlot AS ps
                            WHERE ps.parkingSlotId=?  
                            FOR JSON PATH) AS VARCHAR(MAX))
                            """,(parkingSlotId))
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
        print(f'Exception as getparkingslotdetailsbasedonparkingSlotId {str(e)}')
        return {
            "response": str(e),
            "statusCode": 0
        }


async def getParkingSlotDetailsBasedOnBranchSlotIds(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pll.branchId 
                                     FROM parkingSlot AS ps
                                     INNER JOIN parkingLotLine AS pll
                                     ON pll.parkingLotLineId=ps.parkingLotLineId
                                     WHERE ps.parkingSlotId NOT IN {(tuple(j['slotId'] for i in ast.literal_eval(checkBranchSlotIds[0]) for j in i['us'])+tuple('0'))} AND pll.typeOfVehicle={typeOfVehicle}
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
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
        print("Exception as getParkingSlotDetailsBasedOnBranchSlotIds ",str(e))
        return{"statusCode":0,"response":"Server Error"}
    
async def parkingSlotDetailsBasedOnTypeHFromDateFromTimeToTimefloorIdbranchIdparkingLotLineIdtypeOfVehiclelaneNumber(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        # if type=='H':
        url = f"{os.getenv('BOOKING_URL')}/booking?fromDate={fromDate}&fromTime={fromTime}&toTime={toTime}&floorId={floorId}"
        data = await routers.client.get(url)
        response = json.loads(data.text)  
        await db.execute(f"""SELECT CAST((
                                select pll.parkingLotLineId,pll.branchId,pll.blockId,pll.floorId,pll.parkingOwnerId,pll.typeOfVehicle,
                    pll.noOfRows,pll.noOfColumns,pll.passageLeftAvailable,pll.passageRightAvailable,pll.typeOfParking,pll.activeStatus,
                    pll.vehicleTypeName,pll.typeOfParkingname,pll.vehicleImageUrl,fm.blockName,fm.branchName,fm.parkingName,fm.floorName,
                    (select ps.parkingSlotId,ps.parkingLotLineId,ps.slotNumber,ps.rowId,ps.columnId,ps.isChargeUnitAvailable,ps.chargePinType,ps.laneNumber,
                    ps.activeStatus,ps.slotState,ps.chargePinConfig,ps.chargePinImageUrl,
                    (CASE WHEN EXISTS(select parkingSlot.parkingSlotId from parkingSlot where ps.parkingSlotId NOT IN {tuple(i['slotId'] for i in response['response'])+tuple('0')}
                    )
                                                                            THEN 
                                                                                'available'
                                                                            ELSE
                                                                                'unavailable'
                                                                    END) as slotStatus
                    from parkingSlot as ps where pll.parkingLotLineId=ps.parkingLotLineId and ps.laneNumber='{laneNumber}' and ps.laneNumber='{laneNumber}' ORDER BY slotNumber ASC FOR JSON PATH) as parkingSlotDetails,

                    isnull((SELECT Min(pm.totalAmount) from priceMaster as pm
                                                            WHERE pm.branchId=pll.branchId),0)AS minprice
                    from parkingLotLine as pll
                    inner join floorMaster as fm on fm.floorId=pll.floorId where fm.floorId={floorId} AND fm.branchId={branchId} AND pll.parkingLotLineId={parkingLotLineId} AND pll.typeOfVehicle={typeOfVehicle}
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnTypeHFromDateFromTimeToTimefloorIdbranchIdparkingLotLineIdtypeOfVehiclelaneNumber ",str(e))
        return{"statusCode":0,"response":"Server Error"}  
    
    



async def parkingSlotDetailsBasedOnFromDateFromTimeToTimeBranchId(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        url = f"{os.getenv('BOOKING_URL')}/booking?fromDate={fromDate}&fromTime={fromTime}&toTime={toTime}&branchId={branchId}"
        
        data = await routers.client.get(url)
        response = json.loads(data.text)   
        await db.execute(f"""SELECT CAST((
                                select pll.parkingLotLineId,pll.branchId,pll.blockId,pll.floorId,pll.parkingOwnerId,pll.typeOfVehicle,
                    pll.noOfRows,pll.noOfColumns,pll.passageLeftAvailable,pll.passageRightAvailable,pll.typeOfParking,pll.activeStatus,
                    pll.vehicleTypeName,pll.typeOfParkingname,pll.vehicleImageUrl,fm.blockName,fm.branchName,fm.parkingName,fm.floorName,
                    (select ps.parkingSlotId,ps.parkingLotLineId,ps.slotNumber,ps.rowId,ps.columnId,ps.isChargeUnitAvailable,ps.chargePinType,ps.laneNumber,
                    ps.activeStatus,ps.slotState,ps.chargePinConfig,ps.chargePinImageUrl,
                    (CASE WHEN EXISTS(select parkingSlot.parkingSlotId from parkingSlot where ps.parkingSlotId NOT IN {tuple(i['slotId'] for i in response['response'])+tuple('0')}
                    )
                                                                            THEN 
                                                                                'available'
                                                                            ELSE
                                                                                'unavailable'
                                                                    END) as slotStatus
                    from parkingSlot as ps where pll.parkingLotLineId=ps.parkingLotLineId ORDER BY slotNumber ASC FOR JSON PATH) as parkingSlotDetails,

                    isnull((SELECT Min(pm.totalAmount) from priceMaster as pm
                                                            WHERE pm.branchId=pll.branchId),0)AS minprice
                    from parkingLotLine as pll
                    inner join floorMaster as fm on fm.floorId=pll.floorId
                    where pll.branchId=? and pll.activeStatus='A'
                                            FOR JSON Path) AS  varchar(max))""",(branchId))
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnFromDateFromTimeToTimeBranchId ",str(e))
        return{"statusCode":0,"response":"Server Error"}
    
    
async def parkingSlotDetailsBasedOnFromDateFromTimeToTimeBranchIdTypeOfVehicle(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        url = f"{os.getenv('BOOKING_URL')}/booking?fromDate={fromDate}&fromTime={fromTime}&toTime={toTime}&branchId={branchId}"
        
        data = await routers.client.get(url)
        response = json.loads(data.text)   
        await db.execute(f"""SELECT CAST((
                                select pll.parkingLotLineId,pll.branchId,pll.blockId,pll.floorId,pll.parkingOwnerId,pll.typeOfVehicle,
                    pll.noOfRows,pll.noOfColumns,pll.passageLeftAvailable,pll.passageRightAvailable,pll.typeOfParking,pll.activeStatus,
                    pll.vehicleTypeName,pll.typeOfParkingname,pll.vehicleImageUrl,fm.blockName,fm.branchName,fm.parkingName,fm.floorName,
                    (select ps.parkingSlotId,ps.parkingLotLineId,ps.slotNumber,ps.rowId,ps.columnId,ps.isChargeUnitAvailable,ps.chargePinType,ps.laneNumber,
                    ps.activeStatus,ps.slotState,ps.chargePinConfig,ps.chargePinImageUrl,
                    (CASE WHEN EXISTS(select parkingSlot.parkingSlotId from parkingSlot where ps.parkingSlotId NOT IN {tuple(i['slotId'] for i in response['response'])+tuple('0')}
                    )
                                                                            THEN 
                                                                                'available'
                                                                            ELSE
                                                                                'unavailable'
                                                                    END) as slotStatus
                    from parkingSlot as ps where pll.parkingLotLineId=ps.parkingLotLineId ORDER BY slotNumber ASC FOR JSON PATH) as parkingSlotDetails,

                    isnull((SELECT Min(pm.totalAmount) from priceMaster as pm
                                                            WHERE pm.branchId=pll.branchId),0)AS minprice
                    from parkingLotLine as pll
                    inner join floorMaster as fm on fm.floorId=pll.floorId
                    where pll.branchId=? and pll.activeStatus='A' and pll.typeOfVehicle=?
                                            FOR JSON Path) AS  varchar(max))""",(branchId,typeOfVehicle))
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnFromDateFromTimeToTimeBranchIdTypeOfVehicle ",str(e))
        return{"statusCode":0,"response":"Server Error"}
    
async def parkingSlotDetailsBasedOnFromDateToDateFromTimeToTimeBranchIdTypeOfVehicle(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:

        url = f"{os.getenv('BOOKING_URL')}/booking?fromDate={fromDate}&fromTime={fromTime}&toTime={toTime}&branchId={branchId}&toDate={toDate}"
        data = await routers.client.get(url)
        response = json.loads(data.text)   
        await db.execute(f"""SELECT CAST((
                                select pll.parkingLotLineId,pll.branchId,pll.blockId,pll.floorId,pll.parkingOwnerId,pll.typeOfVehicle,
                    pll.noOfRows,pll.noOfColumns,pll.passageLeftAvailable,pll.passageRightAvailable,pll.typeOfParking,pll.activeStatus,
                    pll.vehicleTypeName,pll.typeOfParkingname,pll.vehicleImageUrl,fm.blockName,fm.branchName,fm.parkingName,fm.floorName,
                    (select ps.parkingSlotId,ps.parkingLotLineId,ps.slotNumber,ps.rowId,ps.columnId,ps.isChargeUnitAvailable,ps.chargePinType,ps.laneNumber,
                    ps.activeStatus,ps.slotState,ps.chargePinConfig,ps.chargePinImageUrl,
                    (CASE WHEN EXISTS(select parkingSlot.parkingSlotId from parkingSlot where ps.parkingSlotId NOT IN {tuple(i['slotId'] for i in response['response'])+tuple('0')}
                    )
                                                                            THEN 
                                                                                'available'
                                                                            ELSE
                                                                                'unavailable'
                                                                    END) as slotStatus
                    from parkingSlot as ps where pll.parkingLotLineId=ps.parkingLotLineId ORDER BY slotNumber ASC FOR JSON PATH) as parkingSlotDetails,

                    isnull((SELECT Min(pm.totalAmount) from priceMaster as pm
                                                            WHERE pm.branchId=pll.branchId),0)AS minprice
                    from parkingLotLine as pll
                    inner join floorMaster as fm on fm.floorId=pll.floorId
                    where pll.branchId=? and pll.activeStatus='A' and pll.typeOfVehicle=?
                                            FOR JSON Path) AS  varchar(max))""",(branchId,typeOfVehicle))
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnFromDateFromTimeToTimeBranchIdTypeOfVehicle ",str(e))
        return{"statusCode":0,"response":"Server Error"}  
    

async def parkingSlotDetailsBasedOnFromDateToDateBranchIdTypeOfVehicle(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        url = f"{os.getenv('BOOKING_URL')}/booking?fromDate={fromDate}&branchId={branchId}&toDate={toDate}"
        
        data = await routers.client.get(url)
        response = json.loads(data.text)   
        await db.execute(f"""SELECT CAST((
                    select pll.parkingLotLineId,pll.branchId,pll.blockId,pll.floorId,pll.parkingOwnerId,pll.typeOfVehicle,
                    pll.noOfRows,pll.noOfColumns,pll.passageLeftAvailable,pll.passageRightAvailable,pll.typeOfParking,pll.activeStatus,
                    pll.vehicleTypeName,pll.typeOfParkingname,pll.vehicleImageUrl,fm.blockName,fm.branchName,fm.parkingName,fm.floorName,
                    (select ps.parkingSlotId,ps.parkingLotLineId,ps.slotNumber,ps.rowId,ps.columnId,ps.isChargeUnitAvailable,ps.chargePinType,ps.laneNumber,
                    ps.activeStatus,ps.slotState,ps.chargePinConfig,ps.chargePinImageUrl,
                    (CASE WHEN EXISTS(select parkingSlot.parkingSlotId from parkingSlot where ps.parkingSlotId NOT IN {tuple(i['slotId'] for i in response['response'])+tuple('0')}
                    )
                                                                            THEN 
                                                                                'available'
                                                                            ELSE
                                                                                'unavailable'
                                                                    END) as slotStatus
                    from parkingSlot as ps where pll.parkingLotLineId=ps.parkingLotLineId ORDER BY slotNumber ASC FOR JSON PATH) as parkingSlotDetails,

                    isnull((SELECT Min(pm.totalAmount) from priceMaster as pm
                                                            WHERE pm.branchId=pll.branchId),0)AS minprice
                    from parkingLotLine as pll
                    inner join floorMaster as fm on fm.floorId=pll.floorId
                    where pll.branchId=? and pll.activeStatus='A' and pll.typeOfVehicle=?
                                            FOR JSON Path) AS  varchar(max))""",(branchId,typeOfVehicle))
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnFromDateToDateBranchIdTypeOfVehicle ",str(e))
        return{"statusCode":0,"response":"Server Error"}
    
 
async def parkingSlotDetailsBasedOnTypeHToDateFromTimeToTimefloorIdbranchIdparkingLotLineIdtypeOfVehiclelaneNumber(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        url = f"{os.getenv('BOOKING_URL')}/booking?fromTime={fromTime}&toTime={toTime}&toDate={toDate}&floorId={floorId}"
        
        data = await routers.client.get(url)
        response = json.loads(data.text)   
        await db.execute(f"""SELECT CAST((
                    select pll.parkingLotLineId,pll.branchId,pll.blockId,pll.floorId,pll.parkingOwnerId,pll.typeOfVehicle,
                    pll.noOfRows,pll.noOfColumns,pll.passageLeftAvailable,pll.passageRightAvailable,pll.typeOfParking,pll.activeStatus,
                    pll.vehicleTypeName,pll.typeOfParkingname,pll.vehicleImageUrl,fm.blockName,fm.branchName,fm.parkingName,fm.floorName,
                    (select ps.parkingSlotId,ps.parkingLotLineId,ps.slotNumber,ps.rowId,ps.columnId,ps.isChargeUnitAvailable,ps.chargePinType,ps.laneNumber,
                    ps.activeStatus,ps.slotState,ps.chargePinConfig,ps.chargePinImageUrl,
                    (CASE WHEN EXISTS(select parkingSlot.parkingSlotId from parkingSlot where ps.parkingSlotId NOT IN {tuple(i['slotId'] for i in response['response'])+tuple('0')}
                    )
                                                                            THEN 
                                                                                'available'
                                                                            ELSE
                                                                                'unavailable'
                                                                    END) as slotStatus
                    from parkingSlot as ps where pll.parkingLotLineId=ps.parkingLotLineId and ps.laneNumber='{laneNumber}' ORDER BY slotNumber ASC FOR JSON PATH) as parkingSlotDetails,

                    isnull((SELECT Min(pm.totalAmount) from priceMaster as pm
                                                            WHERE pm.branchId=pll.branchId),0)AS minprice
                    from parkingLotLine as pll
                    inner join floorMaster as fm on fm.floorId=pll.floorId where fm.floorId={floorId} AND fm.branchId={branchId} AND pll.parkingLotLineId={parkingLotLineId} AND pll.typeOfVehicle={typeOfVehicle}
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnTypeHToDateFromTimeToTimes ",str(e))
        return{"statusCode":0,"response":"Server Error"} 
    
    


async def parkingSlotDetailsBasedOnTypeDFromDatefloorIdbranchIdparkingLotLineIdtypeOfVehiclelaneNumber(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        url = f"{os.getenv('BOOKING_URL')}/booking?fromDate={fromDate}&floorId={floorId}"
        data = await routers.client.get(url)
        response = json.loads(data.text)   
        await db.execute(f"""SELECT CAST((
                    select pll.parkingLotLineId,pll.branchId,pll.blockId,pll.floorId,pll.parkingOwnerId,pll.typeOfVehicle,
                    pll.noOfRows,pll.noOfColumns,pll.passageLeftAvailable,pll.passageRightAvailable,pll.typeOfParking,pll.activeStatus,
                    pll.vehicleTypeName,pll.typeOfParkingname,pll.vehicleImageUrl,fm.blockName,fm.branchName,fm.parkingName,fm.floorName,
                    (select ps.parkingSlotId,ps.parkingLotLineId,ps.slotNumber,ps.rowId,ps.columnId,ps.isChargeUnitAvailable,ps.chargePinType,ps.laneNumber,
                    ps.activeStatus,ps.slotState,ps.chargePinConfig,ps.chargePinImageUrl,
                    (CASE WHEN EXISTS(select parkingSlot.parkingSlotId from parkingSlot where ps.parkingSlotId NOT IN {tuple(i['slotId'] for i in response['response'])+tuple('0')}
                    )
                                                                            THEN 
                                                                                'available'
                                                                            ELSE
                                                                                'unavailable'
                                                                    END) as slotStatus
                    from parkingSlot as ps where pll.parkingLotLineId=ps.parkingLotLineId and ps.laneNumber='{laneNumber}' ORDER BY slotNumber ASC FOR JSON PATH) as parkingSlotDetails,

                    isnull((SELECT Min(pm.totalAmount) from priceMaster as pm
                                                            WHERE pm.branchId=pll.branchId),0)AS minprice
                    from parkingLotLine as pll
                    inner join floorMaster as fm on fm.floorId=pll.floorId where fm.floorId={floorId} AND fm.branchId={branchId} AND pll.parkingLotLineId={parkingLotLineId} AND pll.typeOfVehicle={typeOfVehicle}
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnTypeDFromDate ",str(e))
        return{"statusCode":0,"response":"Server Error"}  
    
    
async def parkingSlotDetailsBasedOnTypeDToDatefloorIdbranchIdparkingLotLineIdtypeOfVehiclelaneNumber(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        url = f"{os.getenv('BOOKING_URL')}/booking?toDate={toDate}&floorId={floorId}"
        data = await routers.client.get(url)
        response = json.loads(data.text)   
        await db.execute(f"""SELECT CAST((
                    select pll.parkingLotLineId,pll.branchId,pll.blockId,pll.floorId,pll.parkingOwnerId,pll.typeOfVehicle,
                    pll.noOfRows,pll.noOfColumns,pll.passageLeftAvailable,pll.passageRightAvailable,pll.typeOfParking,pll.activeStatus,
                    pll.vehicleTypeName,pll.typeOfParkingname,pll.vehicleImageUrl,fm.blockName,fm.branchName,fm.parkingName,fm.floorName,
                    (select ps.parkingSlotId,ps.parkingLotLineId,ps.slotNumber,ps.rowId,ps.columnId,ps.isChargeUnitAvailable,ps.chargePinType,ps.laneNumber,
                    ps.activeStatus,ps.slotState,ps.chargePinConfig,ps.chargePinImageUrl,
                    (CASE WHEN EXISTS(select parkingSlot.parkingSlotId from parkingSlot where ps.parkingSlotId NOT IN {tuple(i['slotId'] for i in response['response'])+tuple('0')}
                    )
                                                                            THEN 
                                                                                'available'
                                                                            ELSE
                                                                                'unavailable'
                                                                    END) as slotStatus
                    from parkingSlot as ps where pll.parkingLotLineId=ps.parkingLotLineId and ps.laneNumber='{laneNumber}' ORDER BY slotNumber ASC FOR JSON PATH) as parkingSlotDetails,

                    isnull((SELECT Min(pm.totalAmount) from priceMaster as pm
                                                            WHERE pm.branchId=pll.branchId),0)AS minprice
                    from parkingLotLine as pll
                    inner join floorMaster as fm on fm.floorId=pll.floorId where fm.floorId={floorId} AND fm.branchId={branchId} AND pll.parkingLotLineId={parkingLotLineId} AND pll.typeOfVehicle={typeOfVehicle}
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnTypeDToDate ",str(e))
        return{"statusCode":0,"response":"Server Error"}  
    
    



async def parkingSlotDetailsBasedOnTypeDFromDateToDatefloorIdbranchIdparkingLotLineIdtypeOfVehiclelaneNumber(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        url = f"{os.getenv('BOOKING_URL')}/booking?toDate={toDate}&fromDate={fromDate}&floorId={floorId}"
        data = await routers.client.get(url)
        response = json.loads(data.text)   
        await db.execute(f"""SELECT CAST((
                    select pll.parkingLotLineId,pll.branchId,pll.blockId,pll.floorId,pll.parkingOwnerId,pll.typeOfVehicle,
                    pll.noOfRows,pll.noOfColumns,pll.passageLeftAvailable,pll.passageRightAvailable,pll.typeOfParking,pll.activeStatus,
                    pll.vehicleTypeName,pll.typeOfParkingname,pll.vehicleImageUrl,fm.blockName,fm.branchName,fm.parkingName,fm.floorName,
                    (select ps.parkingSlotId,ps.parkingLotLineId,ps.slotNumber,ps.rowId,ps.columnId,ps.isChargeUnitAvailable,ps.chargePinType,ps.laneNumber,
                    ps.activeStatus,ps.slotState,ps.chargePinConfig,ps.chargePinImageUrl,
                    (CASE WHEN EXISTS(select parkingSlot.parkingSlotId from parkingSlot where ps.parkingSlotId NOT IN {tuple(i['slotId'] for i in response['response'])+tuple('0')}
                    )
                                                                            THEN 
                                                                                'available'
                                                                            ELSE
                                                                                'unavailable'
                                                                    END) as slotStatus
                    from parkingSlot as ps where pll.parkingLotLineId=ps.parkingLotLineId and ps.laneNumber='{laneNumber}' ORDER BY slotNumber ASC FOR JSON PATH) as parkingSlotDetails,

                    isnull((SELECT Min(pm.totalAmount) from priceMaster as pm
                                                            WHERE pm.branchId=pll.branchId),0)AS minprice
                    from parkingLotLine as pll
                    inner join floorMaster as fm on fm.floorId=pll.floorId where fm.floorId={floorId} AND fm.branchId={branchId} AND pll.parkingLotLineId={parkingLotLineId} AND pll.typeOfVehicle={typeOfVehicle}
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnTypeDFromDateToDate ",str(e))
        return{"statusCode":0,"response":"Server Error"}  

 

#doubt
async def parkingSlotDetailsBasedOnFloorIdLaneNumberActiveStatus(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        # type for getting booking slotsdetails
        Type='S'
        url = f"{os.getenv('BOOKING_URL')}/booking?floorId={floorId}&Type={Type}"
        data = await routers.client.get(url)
        response = json.loads(data.text)   
        await db.execute(f"""SELECT CAST((
                    select pll.parkingLotLineId,pll.branchId,pll.blockId,pll.floorId,pll.parkingOwnerId,pll.typeOfVehicle,
                    pll.noOfRows,pll.noOfColumns,pll.passageLeftAvailable,pll.passageRightAvailable,pll.typeOfParking,pll.activeStatus,
                    pll.vehicleTypeName,pll.typeOfParkingname,pll.vehicleImageUrl,fm.blockName,fm.branchName,fm.parkingName,fm.floorName,
                    (select ps.parkingSlotId,ps.parkingLotLineId,ps.slotNumber,ps.rowId,ps.columnId,ps.isChargeUnitAvailable,ps.chargePinType,ps.laneNumber,
                    ps.activeStatus,ps.slotState,ps.chargePinConfig,ps.chargePinImageUrl,
                    (CASE WHEN EXISTS(select parkingSlot.parkingSlotId from parkingSlot where ps.parkingSlotId NOT IN {tuple(i['slotId'] for i in response['response'])+tuple('0')}
                    )
                                                                            THEN 
                                                                                'available'
                                                                            ELSE
                                                                                'unavailable'
                                                                    END) as slotStatus
                    from parkingSlot as ps where pll.parkingLotLineId=ps.parkingLotLineId and ps.laneNumber='{laneNumber}' ORDER BY slotNumber ASC FOR JSON PATH) as parkingSlotDetails,

                    isnull((SELECT Min(pm.totalAmount) from priceMaster as pm
                                                            WHERE pm.branchId=pll.branchId),0)AS minprice
                    from parkingLotLine as pll
                    inner join floorMaster as fm on fm.floorId=pll.floorId where fm.floorId={floorId} and fm.activeStatus='{activeStatus}'
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnTypeDFromDateToDate ",str(e))
        return{"statusCode":0,"response":"Server Error"}  
    
    
async def parkingSlotDetailsBasedOnFloorId(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        # type for getting booking slotsdetails
        Type='S'
        url = f"{os.getenv('BOOKING_URL')}/booking?floorId={floorId}&Type={Type}"
       
        data = await routers.client.get(url)
        response = json.loads(data.text)   
        await db.execute(f"""SELECT CAST((
                    select pll.parkingLotLineId,pll.branchId,pll.blockId,pll.floorId,pll.parkingOwnerId,pll.typeOfVehicle,
                    pll.noOfRows,pll.noOfColumns,pll.passageLeftAvailable,pll.passageRightAvailable,pll.typeOfParking,pll.activeStatus,
                    pll.vehicleTypeName,pll.typeOfParkingname,pll.vehicleImageUrl,fm.blockName,fm.branchName,fm.parkingName,fm.floorName,
                    (select ps.parkingSlotId,ps.parkingLotLineId,ps.slotNumber,ps.rowId,ps.columnId,ps.isChargeUnitAvailable,ps.chargePinType,ps.laneNumber,
                    ps.activeStatus,ps.slotState,ps.chargePinConfig,ps.chargePinImageUrl,
                    (CASE WHEN EXISTS(select parkingSlot.parkingSlotId from parkingSlot where ps.parkingSlotId NOT IN {tuple(i['slotId'] for i in response['response'])+tuple('0')}
                    )
                                                                            THEN 
                                                                                'available'
                                                                            ELSE
                                                                                'unavailable'
                                                                    END) as slotStatus
                    from parkingSlot as ps where pll.parkingLotLineId=ps.parkingLotLineId ORDER BY slotNumber ASC FOR JSON PATH) as parkingSlotDetails,

                    isnull((SELECT Min(pm.totalAmount) from priceMaster as pm
                                                            WHERE pm.branchId=pll.branchId),0)AS minprice
                    from parkingLotLine as pll
                    inner join floorMaster as fm on fm.floorId=pll.floorId where fm.floorId={floorId}
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnFloorId",str(e))
        return{"statusCode":0,"response":"Server Error"}
    
    
async def parkingSlotDetailsBasedOnFloorIdTypeV(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        #type V for get vehicleType(car.bike,van)  
        await db.execute(f"""SELECT CAST((
                    select DISTINCT fvm.vehicleName from floorVehicleMaster as fvm where 
                                        fvm.floorId={floorId}
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnFloorIdTypeV ",str(e))
        return{"statusCode":0,"response":"Server Error"}
    
    
    


async def parkingSlotDetailsBasedOnFloorIdActiveStatus(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        #type V for get vehicleType(car.bike,van)  
        await db.execute(f"""SELECT CAST((
                    select * from parkingSlotView where floorId={floorId} and activeStatus='{activeStatus}'
                                            FOR JSON Path) AS  varchar(max))""")
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnFloorIdActiveStatus ",str(e))
        return{"statusCode":0,"response":"Server Error"}
    

async def parkingSlotDetailsBasedOnBranchIdActiveStatusTypeOfVehicle(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try: 
        await db.execute(f"""SELECT CAST((
                    select * from parkingSlotView where branchId={branchId} and activeStatus='{activeStatus}' and typeOfVehicle='{typeOfVehicle}'
                                            FOR JSON Path) AS  varchar(max))
                                            """)
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnBranchIdActiveStatusTypeOfVehicle",str(e))
        return{"statusCode":0,"response":"Server Error"}
    

 
    
async def parkingSlotDetailsBasedOnFloorIdActiveStatusTypeOfVehicle(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try: 
        await db.execute(f"""SELECT CAST((
                    select * from parkingSlotView where floorId={floorId} and activeStatus='{activeStatus}' and typeOfVehicle='{typeOfVehicle}'
                                            FOR JSON Path) AS  varchar(max))
                                            """)
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnFloorIdActiveStatusTypeOfVehicle",str(e))
        return{"statusCode":0,"response":"Server Error"}
    

async def parkingSlotDetailsBasedOnBranchIdTypeOfVehicle(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try: 
        await db.execute(f"""SELECT CAST((
                    select * from parkingSlotView where branchId={branchId} and typeOfVehicle='{typeOfVehicle}'
                                            FOR JSON Path) AS  varchar(max))
                                            """)
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnBranchIdTypeOfVehicle",str(e))
        return{"statusCode":0,"response":"Server Error"}
    
async def parkingSlotDetailsBasedOnAll(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try: 
        await db.execute(f"""SELECT CAST((
                    select * from parkingSlotView
                                            FOR JSON Path) AS  varchar(max))
                                            """)
        row = await db.fetchone()
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
        print("Exception as parkingSlotDetailsBasedOnBranchIdTypeOfVehicle",str(e))
        return{"statusCode":0,"response":"Server Error"}

async def parkingSlotDetailsBasedOnBranchIdActiveType(floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db):
    try:
        if Type=='V':
            await db.execute(f"""SELECT CAST((select ps.parkingSlotId,ps.activeStatus,ps.activeStatusName from parkingSlot as ps
                                INNER JOIN parkingLotLine as pl on pl.parkingLotLineId=ps.parkingLotLineId 
                                where pl.branchId=? And ps.activeStatus=?
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
        print("Exception as parkingSlotDetailsBasedOnBranchIdActiveType",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


# parkingSlotDetailsBasedOnFloorIdActiveStatusParkingSlotStatus
# -- fromDate and toDate and fromtime and totime and branchId and typeOfVehicle


slotDict = {
    "floorId=False, branchId=True, activeStatus=True, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=False, fromDate=False, toDate=False, type=False, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnBranchIdAndActiveStatus,
    "floorId=False, branchId=False, activeStatus=False, parkingSlotId=True, checkBranchSlotIds=False, typeOfVehicle=False, fromDate=False, toDate=False, type=False, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":getparkingslotdetailsbasedonparkingSlotId,
    "floorId=False, branchId=False, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=True, typeOfVehicle=True, fromDate=False, toDate=False, type=False, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":getParkingSlotDetailsBasedOnBranchSlotIds,
    
    "floorId=True, branchId=True, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=True, fromDate=True, toDate=False, type=True, fromTime=True, toTime=True, laneNumber=True, parkingSlotStatus=False, parkingLotLineId=True, Type=False":parkingSlotDetailsBasedOnTypeHFromDateFromTimeToTimefloorIdbranchIdparkingLotLineIdtypeOfVehiclelaneNumber,
    "floorId=False, branchId=True, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=False, fromDate=True, toDate=False, type=False, fromTime=True, toTime=True, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnFromDateFromTimeToTimeBranchId,
    "floorId=False, branchId=True, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=True, fromDate=True, toDate=False, type=False, fromTime=True, toTime=True, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnFromDateFromTimeToTimeBranchIdTypeOfVehicle,
    "floorId=False, branchId=True, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=True, fromDate=True, toDate=True, type=False, fromTime=True, toTime=True, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnFromDateToDateFromTimeToTimeBranchIdTypeOfVehicle,
    "floorId=False, branchId=True, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=True, fromDate=True, toDate=True, type=False, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnFromDateToDateBranchIdTypeOfVehicle,
    "floorId=True, branchId=True, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=True, fromDate=False, toDate=True, type=True, fromTime=True, toTime=True, laneNumber=True, parkingSlotStatus=False, parkingLotLineId=True, Type=False":parkingSlotDetailsBasedOnTypeHToDateFromTimeToTimefloorIdbranchIdparkingLotLineIdtypeOfVehiclelaneNumber,
    "floorId=True, branchId=True, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=True, fromDate=True, toDate=False, type=True, fromTime=False, toTime=False, laneNumber=True, parkingSlotStatus=False, parkingLotLineId=True, Type=False":parkingSlotDetailsBasedOnTypeDFromDatefloorIdbranchIdparkingLotLineIdtypeOfVehiclelaneNumber,
    "floorId=True, branchId=True, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=True, fromDate=False, toDate=True, type=True, fromTime=False, toTime=False, laneNumber=True, parkingSlotStatus=False, parkingLotLineId=True, Type=False":parkingSlotDetailsBasedOnTypeDToDatefloorIdbranchIdparkingLotLineIdtypeOfVehiclelaneNumber,
    "floorId=True, branchId=True, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=True, fromDate=True, toDate=True, type=True, fromTime=False, toTime=False, laneNumber=True, parkingSlotStatus=False, parkingLotLineId=True, Type=False":parkingSlotDetailsBasedOnTypeDFromDateToDatefloorIdbranchIdparkingLotLineIdtypeOfVehiclelaneNumber,
    "floorId=True, branchId=False, activeStatus=True, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=False, fromDate=False, toDate=False, type=False, fromTime=False, toTime=False, laneNumber=True, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnFloorIdLaneNumberActiveStatus,
    "floorId=True, branchId=False, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=False, fromDate=False, toDate=False, type=False, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnFloorId,
    "floorId=True, branchId=False, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=False, fromDate=False, toDate=False, type=True, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnFloorIdTypeV,
    "floorId=True, branchId=False, activeStatus=True, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=False, fromDate=False, toDate=False, type=False, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnFloorIdActiveStatus,
    "floorId=False, branchId=True, activeStatus=True, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=True, fromDate=False, toDate=False, type=False, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnBranchIdActiveStatusTypeOfVehicle,
    "floorId=True, branchId=False, activeStatus=True, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=True, fromDate=False, toDate=False, type=False, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnFloorIdActiveStatusTypeOfVehicle,
    "floorId=False, branchId=True, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=True, fromDate=False, toDate=False, type=False, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnBranchIdTypeOfVehicle,
    "floorId=False, branchId=False, activeStatus=False, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=False, fromDate=False, toDate=False, type=False, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=False":parkingSlotDetailsBasedOnAll,
    "floorId=False, branchId=True, activeStatus=True, parkingSlotId=False, checkBranchSlotIds=False, typeOfVehicle=False, fromDate=False, toDate=False, type=False, fromTime=False, toTime=False, laneNumber=False, parkingSlotStatus=False, parkingLotLineId=False, Type=True":parkingSlotDetailsBasedOnBranchIdActiveType,
    

}
#############################################################################################################
@parkingSlotRouter.get('')
async def getparkingSlot(floorId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),activeStatus:Optional[int]=Query(None),parkingSlotId:Optional[int]=Query(None),checkBranchSlotIds:Optional[List]=Query(None),typeOfVehicle:Optional[int]=Query(None),fromDate:Optional[datetime]=Query(None),toDate:Optional[datetime]=Query(None),type:Optional[str]=Query(None),fromTime:Optional[time]=Query(None),toTime:Optional[time]=Query(None),laneNumber:Optional[str]=Query(None),parkingSlotStatus:Optional[str]=Query(None),parkingLotLineId:Optional[int]=Query(None),Type:Optional[str]=Query(None),db:Cursor = Depends(get_cursor)):
    st = f"floorId={True if floorId else False}, branchId={True if branchId else False}, activeStatus={True if activeStatus else False}, parkingSlotId={True if parkingSlotId else False}, checkBranchSlotIds={True if checkBranchSlotIds else False}, typeOfVehicle={True if typeOfVehicle else False}, fromDate={True if fromDate else False}, toDate={True if toDate else False}, type={True if type else False}, fromTime={True if fromTime else False}, toTime={True if toTime else False}, laneNumber={True if laneNumber else False}, parkingSlotStatus={True if parkingSlotStatus else False}, parkingLotLineId={True if parkingLotLineId else False}, Type={True if Type else False}"
    return await slotDict[st](floorId,branchId,activeStatus,parkingSlotId,checkBranchSlotIds,typeOfVehicle,fromDate,toDate,type,fromTime,toTime,laneNumber,parkingSlotStatus,parkingLotLineId,Type,db)


@parkingSlotRouter.post('')
async def postparkingSlot(request:schemas.parkingSlot,db:Cursor = Depends(get_cursor)):
    try:
        r = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.ParkingSlotDetails)
        vehicleDetails=redis_client.hget('vehicleConfigMaster',request.typeOfVehicle)
        typeOfParking = redis_client.hget('configMaster', request.typeOfParking)
        
        typeOfParkingName=typeOfParking.decode("utf-8")  if typeOfParking else None
        data=json.loads(vehicleDetails.decode("utf-8")) if vehicleDetails else None

        if data !=None and typeOfParkingName !=None:
            await db.execute(f""" EXEC [dbo].[postParkingSlot]
                                        @branchId=?,
                                        @blockId=?,
                                        @floorId=?,
                                        @parkingOwnerId=?,
                                        @typeOfVehicle=?,
                                        @vehicleTypeName=?,
                                        @vehicleImageUrl=?,
                                        @noOfRows=?,
                                        @noOfColumns=?,
                                        @passageLeftAvailable=?,
                                        @passageRightAvailable=?,
                                        @typeOfParking=?,
                                        @typeOfParkingname=?,
                                        @activeStatus=?,
                                        @createdBy=?,
                                        @parkingSlotDetailsJson=?""",   
                                        (
                                        request.branchId,
                                        request.blockId,
                                        request.floorId,
                                        request.parkingOwnerId,
                                        request.typeOfVehicle,
                                        data['vehicleTypeName'],
                                        data['vehicleImageUrl'],
                                        request.noOfRows,
                                        request.noOfColumns,
                                        request.passageLeftAvailable,
                                        request.passageRightAvailable,
                                        request.typeOfParking,
                                        typeOfParkingName,
                                        request.activeStatus,
                                        request.createdBy,
                                        json.dumps(r,indent=4,sort_keys=True,default=str)
                                        ))
            row=await db.fetchone()
            await db.commit()
            return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        return{"statusCode":0,"response":str(e)}
    
    
@parkingSlotRouter.put('')
async def putparkingSlot(request:schemas.putparkingSlot,db:Cursor = Depends(get_cursor)):
    try:
        r = Parallel(n_jobs=-1,verbose=True)(delayed(callFunction)(i) for i in request.ParkingSlotDetailsupdate)
        vehicleDetails=redis_client.hget('vehicleConfigMaster',request.typeOfVehicle)
        typeOfParking = redis_client.hget('configMaster', request.typeOfParking)
        
        typeOfParkingName=typeOfParking.decode("utf-8")  if typeOfParking else None
        data=json.loads(vehicleDetails.decode("utf-8")) if vehicleDetails else None
        if data !=None and typeOfParkingName !=None:
            await db.execute(f"""EXEC [dbo].[putparkingSlot]
                                    @parkingLotLineId=?,
                                    @branchId=?,
                                    @blockId=?,
                                    @floorId=?,
                                    @parkingOwnerId=?,
                                    @typeOfVehicle=?,
                                    @vehicleTypeName=?,
                                    @vehicleImageUrl=?,
                                    @noOfRows=?,
                                    @noOfColumns=?,
                                    @passageLeftAvailable=?,
                                    @passageRightAvailable=?,
                                    @typeOfParking=?,
                                    @typeOfParkingname=?,
                                    @activeStatus=?,
                                    @updatedBy=?,
                                    @ParkingSlotDetailsupdateJson=?""",    
                                    (
                                    request.parkingLotLineId,
                                    request.branchId,
                                    request.blockId,
                                    request.floorId,
                                    request.parkingOwnerId,
                                    request.typeOfVehicle,
                                    data['vehicleTypeName'],
                                    data['vehicleImageUrl'],
                                    request.noOfRows,
                                    request.noOfColumns,
                                    request.passageLeftAvailable,
                                    request.passageRightAvailable,
                                    request.typeOfParking,
                                    typeOfParkingName,
                                    request.activeStatus,
                                    request.updatedBy,
                                    json.dumps(r,indent=4, sort_keys=True, default=str)
                                    ))
            row=await db.fetchone()
            await db.commit()
            return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        return{"statusCode":0,"response":str(e)}
    
    
@parkingSlotRouter.delete('')    
async def deleteparkingSlot(activestatus:str,parkingLotLineId:Optional[int]=Query(None),parkingSlotId:Optional[int]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
 
        result=await db.execute(f"""EXEC [dbo].[deleteparkingSlot] ?,?,?""",activestatus,parkingLotLineId,parkingSlotId)
        await db.commit()
        if result.rowcount>=1:
            if activestatus=='A':
                return {
                            "statusCode": 1,
                            "response": "Data Activated Successfully"}
            else:
                return {
                            "statusCode": 1,
                            "response": "Data Inactivated Successfully"}
        else:
            return { "statusCode": 0,
                    "response": "Data Not Found"}
    
    
    except Exception as e:
        return{"statusCode":0,"response":str(e)}


# router = APIRouter(prefix='/parkingSlot',tags=['parkingSlot'])

# async def getparkingslotdetailsbasedonparkingSlotId(parkingSlotId,db):
#     try:
#         data = []              
#         await db.execute(f"""
#                             SELECT CAST((SELECT * 
#                             from parkingSlot AS ps
#                             WHERE ps.parkingSlotId=?  
#                             FOR JSON PATH) AS VARCHAR(MAX))
#                             """,(parkingSlotId))
#         row = await db.fetchone()
#         if row[0] != None:           
#             data=(json.loads(row[0]))
#             return {
#             "response":data,
#             "statusCode":1
#         }                
#         return {
#             "response":"data not found",
#             "statusCode":0
#         }
#     except Exception as e:
#         print(f'error {str(e)}')
#         return {
#             "response": str(e),
#             "statusCode": 0
#         }

# parkingslotDict = {
#     "parkingSlotId=True":getparkingslotdetailsbasedonparkingSlotId
# }

# ##################################################################################################################
# @router.get('')
# async def parkingslotGet(parkingSlotId:Optional[int]=Query(None), db:Cursor = Depends(get_cursor)):
#     st = f"parkingSlotId={True if parkingSlotId else False}"
#     return await parkingslotDict[st](parkingSlotId, db)

