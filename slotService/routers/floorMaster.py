from fastapi import Query
from fastapi.routing import APIRouter
from typing import Optional
from fastapi import Depends
from aioodbc.cursor import Cursor
import json
import routers
import os
from dotenv import load_dotenv
from routers.config import get_cursor,redis_client
import schemas
from joblib import Parallel, delayed
import asyncio
from task import postFloorName

load_dotenv()

floorRouter = APIRouter(prefix='/floorMaster',tags=['floorMaster'])
def callFunction(i):
    return i.dict()

def VehicleMasterCallFunction(i):
    i=i.dict()
    vehicleDetails=redis_client.hget('vehicleConfigMaster', i['vehicleType'])
    i['vehicleTypeName'],i['vehicleImageUrl'],i['vehiclePlaceHolderImageUrl']=tuple(json.loads(vehicleDetails.decode("utf-8")).values()) if vehicleDetails else None
    return i

async def floorDetailsBasedOnFloorId(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.floorId=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(floorId))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnFloorId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        

async def floorDetailsBasedOnFloorIdAndActiveStatus(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.floorId=? and fm.activeStatus=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnFloorIdAndActiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def floorDetailsBasedOnparkingOwnerIdAndbranchIdAndActiveStatus(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.branchId=? and fm.activeStatus=? and fm.parkingOwnerId=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(branchId,activeStatus,parkingOwnerId))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnparkingOwnerIdAndbranchIdAndActiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        
async def floorDetailsBasedOnparkingOwnerId(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.parkingOwnerId=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(parkingOwnerId))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnparkingOwnerId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        


async def floorDetailsBasedOnbranchId(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.branchId=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(branchId))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnbranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        
        

async def floorDetailsBasedOnblockIdAndActiveStatus(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.blockId=? and fm.activeStatus=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(blockId,activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnblockIdAndActiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        
        
async def floorDetailsBasedOnblockId(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.blockId=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(blockId))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnblockId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        
        
async def floorDetailsBasedOnActiveStatus(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.activeStatus=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnActiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }



async def floorDetailsBasedOnfloorName(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.floorName=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(floorName))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnfloorName ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }  
        
        
async def floorDetailsBasedOnfloorType(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.floorType=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(floorType))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnfloorType ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        } 
        
async def floorDetailsBasedOnfloorTypeAndActiveStatus(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.floorType=? and fm.activeStatus=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(floorType,activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnfloorTypeAndActiveStatus",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }   
 
async def floorDetailsBasedOnbranchIdAndActivestatus(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    
    try:
        await db.execute(f"""SELECT CAST((SELECT CAST((SELECT fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,
                                        (SELECT MIN(priceMaster.totalAmount)FROM floorMaster 
                                        INNER JOIN priceMaster ON priceMaster.floorId = floorMaster.floorId
                                        INNER JOIN floorVehicleMaster AS fvm
                                        ON fm.floorId=fvm.floorId
                                        WHERE floorMaster.branchId =?
                                        AND priceMaster.branchId=floorMaster.branchId AND priceMaster.idType='V')AS minprice
                                        FROM floorMaster as fm
                                        WHERE fm.branchId=? AND fm.activeStatus=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(branchId,branchId,activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorDetailsBasedOnbranchIdAndActivestatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        
async def allDetails(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        await db.execute(f"""SELECT CAST((select fm.floorId,fm.parkingOwnerId,fm.parkingName,fm.branchId,fm.branchName,fm.blockId,fm.blockName,fm.squareFeet,fm.floorName as floorNameId,fm.floorConfigName as floorName,
                                        fm.floorType,fm.floorTypeName,fm.activeStatus,(select fvm.floorVehicleId,fvm.floorId,fm.floorConfigName,fvm.vehicleType,fvm.vehicleTypeName,fvm.vehicleImageUrl,
                                        fvm.capacity,fvm.length,fvm.height,fvm.rules,fvm.activeStatus,fm.floorName from 
                                        floorVehicleMaster as fvm 
										inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.floorId=fvm.floorId for json path) as floorVehicleDetails,
                                        (select ff.featuresId,ff.featureName,ff.parkingOwnerId,fm.parkingName,ff.branchId,fm.branchName,ff.floorId,
                                        fm.floorName,ff.description,ff.amount,ff.taxId,ff.tax,ff.taxName,ff.totalAmount,
                                        ff.activeStatus from floorFeatures as ff
										inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=fm.floorId for json path) as floorFeaturesDetails from floorMaster as fm
                                        where fm.floorType=? and fm.activeStatus=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""",(floorType,activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:           
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as allDetails",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        } 
    

async def floorDetailsBasedOnbranchIdTypeActiveStatusvehicleType(floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db):
    try:
        if type=='P':
            await db.execute(f"""SELECT CAST((
                SELECT fm.blockId, fm.blockName, fm.floorId, fm.floorName FROM floorMaster as fm
                            WHERE fm.floorId IN (SELECT DISTINCT floorId FROM parkingLotLine as pll WHERE pll.typeOfVehicle={vehicleType})
                                AND fm.branchId ={branchId} AND fm.activeStatus ='{activeStatus}'
                                        FOR JSON PATH) AS VARCHAR(MAX))""")
            row = await db.fetchone()
            if row[0] != None:
                data=(json.loads(row[0]))                
                return {
                    "response":data,
                    "statusCode":1
                    }
            else:           
                return {
                    "response":"Data Not Found",
                    "statusCode":0
                }
    except Exception as e:
        print("Exception as floorDetailsBasedOnbranchIdTypeActiveStatusvehicleType ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

floorDict = {
    "floorId=True,branchId=False,parkingOwnerId=False,blockId=False,floorName=False,floorType=False,activeStatus=False,type=False,vehicleType=False":floorDetailsBasedOnFloorId,
    "floorId=False,branchId=True,parkingOwnerId=False,blockId=False,floorName=False,floorType=False,activeStatus=True,type=False,vehicleType=False":floorDetailsBasedOnbranchIdAndActivestatus,
    "floorId=True,branchId=False,parkingOwnerId=False,blockId=False,floorName=False,floorType=False,activeStatus=True,type=False,vehicleType=False":floorDetailsBasedOnFloorIdAndActiveStatus,
    "floorId=False,branchId=True,parkingOwnerId=True,blockId=False,floorName=False,floorType=False,activeStatus=True,type=False,vehicleType=False":floorDetailsBasedOnparkingOwnerIdAndbranchIdAndActiveStatus,
    "floorId=False,branchId=False,parkingOwnerId=True,blockId=False,floorName=False,floorType=False,activeStatus=False,type=False,vehicleType=False":floorDetailsBasedOnparkingOwnerId,
    "floorId=False,branchId=True,parkingOwnerId=False,blockId=False,floorName=False,floorType=False,activeStatus=False,type=False,vehicleType=False":floorDetailsBasedOnbranchId,
    "floorId=False,branchId=False,parkingOwnerId=False,blockId=True,floorName=False,floorType=False,activeStatus=False,type=False,vehicleType=False":floorDetailsBasedOnblockId,
    "floorId=False,branchId=False,parkingOwnerId=False,blockId=True,floorName=False,floorType=False,activeStatus=True,type=False,vehicleType=False":floorDetailsBasedOnblockIdAndActiveStatus,
    "floorId=False,branchId=False,parkingOwnerId=False,blockId=False,floorName=False,floorType=False,activeStatus=True,type=False,vehicleType=False":floorDetailsBasedOnActiveStatus,
    "floorId=False,branchId=False,parkingOwnerId=False,blockId=False,floorName=True,floorType=False,activeStatus=False,type=False,vehicleType=False":floorDetailsBasedOnfloorName,
    "floorId=False,branchId=False,parkingOwnerId=False,blockId=False,floorName=False,floorType=True,activeStatus=False,type=False,vehicleType=False":floorDetailsBasedOnfloorType,
    "floorId=False,branchId=False,parkingOwnerId=False,blockId=False,floorName=False,floorType=True,activeStatus=True,type=False,vehicleType=False":floorDetailsBasedOnfloorTypeAndActiveStatus,
    "floorId=False,branchId=False,parkingOwnerId=False,blockId=False,floorName=False,floorType=False,activeStatus=False,type=False,vehicleType=False":allDetails,
    "floorId=False,branchId=True,parkingOwnerId=False,blockId=False,floorName=False,floorType=False,activeStatus=True,type=True,vehicleType=True":floorDetailsBasedOnbranchIdTypeActiveStatusvehicleType

}

##################################################################################################################
@floorRouter.get('')
async def floorGet(floorId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None),blockId:Optional[int]=Query(None),floorName:Optional[int]=Query(None),floorType:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),type:Optional[str]=Query(None),vehicleType:Optional[str]=Query(None), db:Cursor = Depends(get_cursor)):
    try:
        st = f"floorId={True if floorId else False},branchId={True if branchId else False},parkingOwnerId={True if parkingOwnerId else False},blockId={True if blockId else False},floorName={True if floorName else False},floorType={True if floorType else False},activeStatus={True if activeStatus else False},type={True if type else False},vehicleType={True if vehicleType else False}"
        return await floorDict[st](floorId,branchId,parkingOwnerId,blockId,floorName,floorType,activeStatus,type,vehicleType, db)
    except Exception as e:
        print("Exception as floorGet ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@floorRouter.post('')
async def postfloorMaster(request:schemas.FloorMaster,db:Cursor = Depends(get_cursor)):
    try:
        if request.floorVehicleMasterDetails!=None:
                floorVehicleMasterJson = Parallel(n_jobs=-1, verbose=True)(delayed(VehicleMasterCallFunction)(i) for i in request.floorVehicleMasterDetails)
                floorVehicleMasterJson=json.dumps(floorVehicleMasterJson)
        else:
            floorVehicleMasterJson=None
        if request.floorFeaturesDetails!=None:
            floorFeaturesDetailsJson = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.floorFeaturesDetails)
            floorFeaturesDetailsJson=json.dumps(floorFeaturesDetailsJson)
        else:
            floorFeaturesDetailsJson=None

        
        floorName = redis_client.hget('configMaster', request.floorName)
        parkingName = redis_client.hget('parkingOwnerMaster', request.parkingOwnerId)
        branchName = redis_client.hget('branchMaster', request.branchId)
        blockName = redis_client.hget('blockMaster', request.blockId)
        floorTypeName = redis_client.hget('configMaster', request.floorType)
        
        floorName=floorName.decode("utf-8")  if floorName else None
        parkingName=parkingName.decode("utf-8") if parkingName else None
        branchName=branchName.decode("utf-8")  if branchName else None
        blockName=blockName.decode("utf-8") if blockName else None
        floorTypeName=floorTypeName.decode("utf-8")  if floorTypeName else None
        print("hi")
        await db.execute(f"""
                        DECLARE @varRes NVARCHAR(400);
                        DECLARE @varStatus NVARCHAR(1);
                        DECLARE @varfloorId  INT;
                        EXEC [dbo].[postFloorMaster] 
                        @parkingOwnerId=?,
                        @parkingName=?,
                        @branchId=?,
                        @branchName=?,
                        @blockId=?,
                        @blockName=?,
                        @floorName=?,
                        @floorConfigName=?,
                        @floorType=?,
                        @floorTypeName=?,
                        @squareFeet=?,
                        @activeStatus=?,
                        @createdBy=?,
                        @floorVehicleMasterJson=?,
                        @floorFeaturesJson=?,
                        @outputVal = @varRes OUTPUT,
                        @outputStatus = @varStatus OUTPUT,
                        @floorIds=@varfloorId OUTPUT
                        SELECT @varRes AS varRes,@varStatus AS varStatus,@varfloorId AS floorId
                      """,
                      (request.parkingOwnerId,
                        parkingName,
                        request.branchId,
                        branchName,
                        request.blockId,
                        blockName,
                        request.floorName,
                        floorName,
                        request.floorType,
                        floorTypeName,
                        request.squareFeet,
                        request.activeStatus,
                        request.createdBy,
                        floorVehicleMasterJson,
                        floorFeaturesDetailsJson))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            postFloorName.delay(int(row[2]),floorName)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}
      

    except Exception as e:
        print("Exception as postfloorMaster ",str(e))
        return{"statusCode":0,"response":str(e)}

@floorRouter.put('')
async def putfloorMaster(request:schemas.PutFloorMaster,db:Cursor = Depends(get_cursor)):
    try:
        floorName = redis_client.hget('configMaster', request.floorName)
        floorTypeName = redis_client.hget('configMaster', request.floorType)
        
        floorName=floorName.decode("utf-8")  if floorName else None
        floorTypeName=floorTypeName.decode("utf-8")  if floorTypeName else None
        await db.execute("""
                               EXEC [dbo].[putfloorMaster] 
                               @floorId=?,
                               @floorConfigName=?
                               @squareFeet=?,
                               @floorName=?,
                               @floorType=?,
                               @floorTypeName=?,
                               @activeStatus=?,
                               @updatedBy=?
                               """,
                                (
                                 request.floorId,
                                 floorName,
                                 request.squareFeet,
                                 request.floorName,
                                 request.floorType,
                                 floorTypeName,
                                 request.activeStatus,
                                 request.updatedBy
                                ))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            postFloorName.delay(request.floorId,floorName)
            return{"statusCode":int(row[1]),"response":row[0]}
        else:
            return{"statusCode":int(row[1]),"response":row[0]}
    
    except Exception as e:
        print("Exception as putfloorMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}
    
    
@floorRouter.delete('')    
async def deletefloorMaster(floorId:int,activeStatus:str,db:Cursor = Depends(get_cursor)):
    try:
 
        result=await db.execute("UPDATE floorMaster SET activeStatus=? WHERE floorId=?",activeStatus,floorId)
        await db.commit()
        if result.rowcount>=1:
            if activeStatus=='A':
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
        print("Exception as deletefloorMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}

        

