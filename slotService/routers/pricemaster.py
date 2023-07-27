from re import A
from fastapi import Query
from fastapi.routing import APIRouter
from typing import Optional,List
from routers.config import get_cursor,redis_client 
from fastapi import Depends
from aioodbc.cursor import Cursor
import json,os,ast
import routers
from dotenv import load_dotenv
import schemas
import asyncio
import ast
load_dotenv()

router = APIRouter(prefix='/priceMaster',tags=['priceMaster'])
 

async def getPriceTaxId(taxId):
    try:
        response = await routers.client.get(f"{os.getenv('ADMIN_SERVICE_URL')}/taxMaster?taxId={taxId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            
            return response['response'][0]
        return ""
    except Exception as e:
        print("Exception as getPriceTaxId ",str(e))
        return ""
    
async def getConfigTypeName(configId):
    try:
        
        url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configId={configId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0]
            
        return ""
    except Exception as e:
        print("Exception as getConfigName ",str(e))
        return ""

async def getConfigName(floorName):
    try:
        
        url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configId={floorName}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0]['configName']
            
        return ""
    except Exception as e:
        print("Exception as getConfigName ",str(e))
        return ""
    



async def getBranchName(branchId):
    try:
        
        url=f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/branchMaster?branchId={branchId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0] 
        return ""
    except Exception as e:
        print("Exception as getBranchName ",str(e))
        return ""
async def getVehicleName(vehicleConfigId):
    try:
        
        url=f"{os.getenv('ADMIN_SERVICE_URL')}/vehicleConfigMaster?vehicleConfigId={vehicleConfigId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0]['vehicleName']
        return ""
    except Exception as e:
        print("Exception as getVehicleName ",str(e))
        return ""

async def modifiedDataFloorName(floorName, dic):
    dic['floorName'] = await getConfigName(floorName)

async def modifiedDataBranchName(branchId, dic):
    branchDetails=await getBranchName(branchId)
    dic['branchName'] = branchDetails['branchName']
    dic['parkingName'] = branchDetails['parkingName']

async def modifiedDataTaxName(taxId, dic):
    taxDetails = await getPriceTaxId(taxId)
    dic['taxName']=taxDetails['taxName']
    dic['taxPercentage']=taxDetails['taxPercentage']

async def modifiedDataVehicleAccessoriesName(vehicleAccessories,idType, dic):
    if idType=='V':
        dic['vehicleAccessoriesName'] = await getVehicleName(vehicleAccessories)
    elif idType=='A':
        dic['vehicleAccessoriesName'] = await getConfigName(vehicleAccessories)
        
        
async def modifiedDataConfitypeName(floorName, dic):
    dic['floorName'] = await getConfigTypeName(floorName)

async def getpriceDetails(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):

    try:        
        await db.execute(f"""
                            SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                            FOR JSON PATH) AS VARCHAR(MAX))
                            """)
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
        print("Exception as getpriceDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getPriceDetailsBasedOnTaxId(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    try:
        await db.execute(f"""SELECT CAST(MAX(pm.createdDate) as date)AS priceMaster
                                FROM priceMaster AS pm
                                WHERE pm.taxId = ?
                                """, (taxId))
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
        print("Exception as getPriceDetailsBasedOnTaxId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getpriceDetailsBasedOnfloorIdandIdtypeandtimetypeandactiveStatus(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    try:
        data = []
        url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
        response = await routers.client.get(url)
        var = json.loads(response.text)
        url1=f"{os.getenv('BOOKING_URL')}/vehicleHeader"
        response1 = await routers.client.get(url1)
        var1 = json.loads(response1.text)
        if var['statusCode']==1 and var1['statusCode']==1: 
            for id in var['response']:
                for id1 in var1['response']:
                    await db.execute(f"""
                                        SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                            pm.[vehicle/accessories],pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                            pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime
                                             from priceMaster as pm
                                            WHERE pm.floorId=? and pm.timetype=? and pm.idType=? and pm.activeStatus=? and pm.[vehicle/accessories]={id1['vehicleType']} and pm.userMode=(SELECT(CASE WHEN(SELECT '{id['configName']}' WHERE {id['configId']} IN (SELECT activeStatus FROM parkingSlot  as ps WHERE ps.parkingSlotId={id1['slotId']}))='VIP' THEN 'V' ELSE 'N' END))
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                        """,(floorId,timetype,idType,activeStatus))
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
        print("Exception as getpriceDetailsBasedOnfloorIdandIdtypeandtimetypeandactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getpriceDetailsBasedOnbranchIdandIdtypeandtimetypeandactiveStatus(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                            WHERE pm.branchId=? and pm.timetype=? and pm.idType=? and pm.activeStatus=?
                            FOR JSON PATH) AS VARCHAR(MAX))
                            """,(branchId,timetype,idType,activeStatus))
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
        print("Exception as getpriceDetailsBasedOnbranchIdandIdtypeandtimetypeandactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getpriceDetailsBasedOnparkingOwnerIdandIdtypeandtimetypeandactiveStatus(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                            WHERE pm.parkingOwnerId=? and pm.timetype=? and pm.idType=? and pm.activeStatus=?
                            FOR JSON PATH) AS VARCHAR(MAX))
                            """,(parkingOwnerId,timetype,idType,activeStatus))
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
        print("Exception as getpriceDetailsBasedOnparkingOwnerIdandIdtypeandtimetypeandactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getpriceDetailsBasedOnuserIdandIdtypeandtimetypeandactiveStatus(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:
        url = f"{os.getenv('BOOKING_URL')}/booking?userId={userId}"
        response = await routers.client.get(url)
        var = json.loads(response.text)
        url1=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
        response1 = await routers.client.get(url1)
        var1 = json.loads(response1.text)
        url2=f"{os.getenv('BOOKING_URL')}/vehicleHeader"
        response2 = await routers.client.get(url2)
        var2 = json.loads(response2.text)
        if var['statusCode']==1 and var1['statusCode']==1 and var2['statusCode']==1: 
            for id in var1['response']:
                for id1 in var2['response']:
                    await db.execute(f"""
                                        SELECT CAST((SELECT pm.*
                                            FROM priceMaster AS pm
                                            INNER JOIN floorMaster AS fm
                                            ON fm.floorId=pm.floorId
                                            WHERE pm.timetype=? and pm.idType=? and pm.activeStatus=? and pm.[vehicle/accessories]={id1['vehicleType']} and pm.userMode=(SELECT(CASE WHEN(SELECT '{id['configName']}' WHERE {id['configId']} IN (SELECT activeStatus FROM parkingSlot  as ps WHERE ps.parkingSlotId={id1['slotId']}))='VIP' THEN 'V' ELSE 'N' END))
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                        """,(timetype,idType,activeStatus))
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
        print("Exception as getpriceDetailsBasedOnuserIdandIdtypeandtimetypeandactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getpriceDetailsBasedOnblockIdandIdtypeandtimetypeandactiveStatus(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    try:
        data = []
        url=f"{os.getenv('ADMIN_SERVICE_URL')}/configMaster?configTypeName=slotType"
        response = await routers.client.get(url)
        var = json.loads(response.text)
        url1=f"{os.getenv('BOOKING_URL')}/vehicleHeader"
        response1 = await routers.client.get(url1)
        var1 = json.loads(response1.text)
        if var['statusCode']==1 and var1['statusCode']==1: 
            for id in var['response']:
                for id1 in var1['response']:
                    await db.execute(f"""
                                        SELECT CAST((SELECT pm.*
                                            FROM priceMaster AS pm
                                            INNER JOIN floorMaster AS fm
                                            ON fm.floorId=pm.floorId 
                                            WHERE fm.blockId=? and pm.timetype=? and pm.idType=? and pm.activeStatus=? and pm.userMode=(SELECT(CASE WHEN(SELECT '{id['configName']}' WHERE {id['configId']} IN (SELECT activeStatus FROM parkingSlot  as ps WHERE ps.parkingSlotId={id1['slotId']}))='VIP' THEN 'V' ELSE 'N' END))
                                        FOR JSON PATH) AS VARCHAR(MAX))
                                        """,(blockId,timetype,idType,activeStatus))
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
        print("Exception as getpriceDetailsBasedOnfloorIdandIdtypeandtimetypeandactiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

async def getpriceDetailsIdtypeandtimetypeandactiveStatus(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    try:
        data = []
        await db.execute(f"""
                            SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                            WHERE pm.timetype=? and pm.idType=? and pm.activeStatus=?
                            FOR JSON PATH) AS VARCHAR(MAX))
                            """,(timetype,idType,activeStatus))
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
        print("Exception as getpriceDetailsIdtypeandtimetypeandactiveStatus",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getpriceDetailsbasedonbranchIdandIdType(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    try:
        data = []
        if idType=='A':
            await db.execute(f"""
                                SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.branchId=? and pm.idType=?
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """,(branchId,idType))
        elif idType=='V':
            await db.execute(f"""
                                SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName,ISNULL(Min(pm.totalAmount),0)as minPrice from priceMaster as pm
                                WHERE pm.branchId=? and pm.idType=?
                                GROUP BY pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] ,pm.[vehicle/accessoriesName],
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName
                                FOR JSON PATH) AS VARCHAR(MAX))
                                """,(branchId,idType))
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
        print("Exception as getpriceDetailsbasedonbranchIdandIdType ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }


async def getPriceDetailsBasedOnFloorId(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST(( select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.floorId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(floorId))
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
        print("Exception as getPriceDetailsBasedOnFloorId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getPriceDetailsBasedOnFloorIdUserMode(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST(( select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.floorId=? AND pm.userMode=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,userMode))
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
        print("Exception as getPriceDetailsBasedOnFloorIdUserMode ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def getPriceDetailsBasedOnBranchId(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.branchId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(branchId))
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
        print("Exception as getPriceDetailsBasedOnBranchId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def getPriceDetailsBasedOnActiveStatus(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.activeStatus=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus))
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
        print("Exception as getPriceDetailsBasedOnActiveStatus",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
async def getPriceDetailsBasedOnPriceIdActiveStatus(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.activeStatus=? AND pm.priceId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus,priceId))
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
        print("Exception as getPriceDetailsBasedOnPriceIdActiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def getPriceDetailsBasedOnBranchParkingOwnerActiveId(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST(( select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.branchId=? AND pm.activeStatus=? AND pm.parkingOwnerId=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(branchId,activeStatus,parkingOwnerId))
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
        print("Exception as getPriceDetailsBasedOnBranchParkingOwnerActiveId",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def getPriceDetailsBasedOnFloorTimeTypeActiveId(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST(( select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.floorId=? AND pm.activeStatus=? AND pm.timetype=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,activeStatus,timetype))
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
        print("Exception as getPriceDetailsBasedOnFloorTimeTypeActiveId",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def getPriceDetailsBasedOnFloorIdTypeActiveId(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.floorId=? AND pm.activeStatus=? AND pm.idType=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,activeStatus,idType))
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
        print("Exception as getPriceDetailsBasedOnFloorIdTypeActiveId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getPriceDetailsBasedOnFloorTimeIdTypeActiveUserMode(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.floorId=? AND pm.activeStatus=? AND pm.timetype=? AND pm.idType=? AND pm.userMode=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,activeStatus,timetype,idType,userMode))
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
        print("Exception as getPriceDetailsBasedOnFloorTimeIdTypeActiveUserMode ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def getPriceDetailsBasedOnFloorTimeIdTypeActiveUserModeVehicleAccessories(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.floorId=? AND pm.activeStatus=? AND pm.timetype=? AND pm.idType=? AND pm.userMode=? AND pm.vehicleAccessories=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,activeStatus,timetype,idType,userMode,vehicleAccessories))
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
        print("Exception as getPriceDetailsBasedOnFloorTimeIdTypeActiveUserModeVehicleAccessories ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def getPriceDetailsBasedOnFloorTimeTypeActiveUserMode(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.floorId=? AND pm.activeStatus=? AND pm.timetype=? AND pm.userMode=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,activeStatus,timetype,userMode))
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
        print("Exception as getPriceDetailsBasedOnFloorTimeTypeActiveUserMode ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getPriceDetailsBasedOnFloorIdTypeActiveUserMode(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.floorId=? AND pm.activeStatus=? AND pm.idtype=? AND pm.userMode=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,activeStatus,idType,userMode))
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
        print("Exception as getPriceDetailsBasedOnFloorIdTypeActiveUserMode ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def getPriceDetailsBasedOnFloorIdIdType(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST((SELECT *,
							(CASE WHEN pm.timeType = 'H'
									THEN 'Hourly'
								  WHEN pm.timeType= 'D'
									THEN 'Daily'
								  WHEN pm.timeType = 'EH'
									THEN 'Extended Hourly'
								  WHEN pm.timeType = 'ED'
									THEN 'Extended Daily'
									ELSE
										'TimeSlab'
									END) as timeTypeFullForm
							
							FROM priceMasterView as pm
                                FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,idType))
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
        print("Exception as getPriceDetailsBasedOnFloorIdTypeActiveUserMode ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getPriceIdsDetails(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    try: 
        print(priceIds)
        for i in ast.literal_eval(priceIds[0]): 
            print(i['count'])      
            await db.execute(f"""SELECT CAST((SELECT ISNULL(SUM(pm.totalAmount *{i['count']}),0) AS extraFeesTotalAmount,ISNULL(SUM(pm.Amount *{i['count']}),0) AS extraFeesAmount,ISNULL(SUM(pm.tax *{i['count']}),0) AS extraFeesTaxAmount
                                                FROM priceMaster as pm
                                                WHERE pm.priceId IN {tuple(i['priceId'] for i in ast.literal_eval(priceIds[0]))+tuple('0')}
                                            FOR JSON PATH) AS VARCHAR(MAX))
                        """)
        row = await db.fetchone()
        print("row",row)
        if row[0] != None:  
            return {
                "response":json.loads(row[0]),
                "statusCode":1
                }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as getPriceIdsDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        

# activeStatus & floorId & usermode & idType & vehicleAccessories


async def getPriceDetailsBasedOnActiveStatusFloorIdUsermodeIdTypeVehicleAccessories(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.floorId=? AND pm.activeStatus=? AND pm.idType=? AND pm.userMode=? AND pm.[vehicle/accessories]=?
                                FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,activeStatus,idType,userMode,vehicleAccessories))
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
        print("Exception as getPriceDetailsBasedOnFloorTimeTypeActiveUserMode ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        



async def getPriceDetailsBasedOnActiveStatusFloorIdIdTypeConfigTypeId(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                WHERE pm.floorId=? AND pm.activeStatus=? AND pm.idType=? AND pm.configTypeId=? 
                                FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,activeStatus,idType,configTypeId))
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
        print("Exception as getPriceDetailsBasedOnActiveStatusFloorIdIdTypeConfigTypeId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        




async def getPriceDetailsBasedOnActiveStatusFloorIdIdTypeVehicleConfigId(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:
        url1 = f"{os.getenv('ADMIN_SERVICE_URL')}/vehicleConfigMaster?vehicleConfigId={vehicleConfigId}&type=A"
        response1 = await routers.client.get(url1)
        var1= json.loads(response1.text)
        if var1['statusCode']==1:  
            await db.execute(f"""SELECT CAST((select pm.priceId,pm.parkingOwnerId,pm.parkingName,pm.branchId,pm.branchName,pm.floorId,pm.floorName,pm.amount,pm.tax,pm.totalAmount,pm.idType,
                                    pm.[vehicle/accessories] as vehicleAccessories,pm.[vehicle/accessoriesName] as vehicleAccessoriesName,
                                    pm.timeType,pm.taxId,pm.taxName,pm.userMode,pm.activeStatus,pm.remarks,pm.graceTime,pm.configTypeId,pm.configTypeName from priceMaster as pm
                                    WHERE pm.floorId=? AND pm.activeStatus=? AND pm.idType=? AND pm.[vehicle/accessoriesName] IN {(tuple(i['configId'] for i in var1['response']))}
                                    FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,activeStatus,idType))
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
        print("Exception as getPriceDetailsBasedOnActiveStatusFloorIdIdTypeVehicleConfigId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def getPriceDetailsBasedOnFloorIdIdTypeType(floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db):
    data=[]
    try:        
        await db.execute(f"""SELECT CAST((SELECT fm.floorId, fm.parkingOwnerId, fm.parkingName,fm.branchId, fm.branchName , fm.floorName, 
										( SELECT TOP 1 graceTime FROM priceMaster  as pms WHERE pms.floorId = fm.floorId AND pms.idType='{idType}') as graceTime, 
										( SELECT TOP 1 idType FROM priceMaster as pms WHERE pms.floorId = fm.floorId AND pms.idType='{idType}') as idType, 
										a.[vehicle/accessories] as vehicleAccessories , 
										
									(select top 1 [vehicle/accessoriesName] from priceMaster where [vehicle/accessories]=a.[vehicle/accessories] and idType='{idType}') as vehicleAccessoriesName,
									(SELECT TOP 1 activeStatus FROM priceMaster as pms WHERE pms.floorId= fm.floorId AND pms.userMode='V' AND pms.[vehicle/accessories] = a.[vehicle/accessories]) as activeStatus,
									(SELECT pms.priceId,pms.timeType, pms.totalAmount, pms.tax, (pms.totalAmount - pms.tax) as amount,pms.userMode, pms.activeStatus 
										FROM priceMaster as pms
										WHERE pms.floorId = fm.floorId AND pms.idType='{idType}' AND pms.[vehicle/accessories] = a.[vehicle/accessories] FOR JSON PATH) as priceDetails,
									(SELECT TOP 1 taxId FROM priceMaster as pm WHERE pm.floorId = fm.floorId AND pm.[vehicle/accessories] = a.[vehicle/accessories]) as taxId
								FROM floorMaster as fm
								CROSS APPLY (SELECT DISTINCT [vehicle/accessories] FROM priceMaster as pm WHERE pm.floorId = fm.floorId AND pm.idType = '{idType}') as a
								WHERE fm.floorId=?
								FOR JSON PATH, INCLUDE_NULL_VALUES) AS VARCHAR(MAX))""",(floorId))
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
        print("Exception as getPriceDetailsBasedOnActiveStatusFloorIdIdTypeConfigTypeId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }



priceMasterDict = {
    "floorId=False, branchId=False, timetype=False, idType=False, activeStatus=False, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getpriceDetails,
    "floorId=False, branchId=False, timetype=False, idType=False, activeStatus=False, parkingOwnerId=False, taxId=True, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnTaxId,
    "floorId=True, branchId=False, timetype=True, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getpriceDetailsBasedOnfloorIdandIdtypeandtimetypeandactiveStatus,
    "floorId=False, branchId=True, timetype=True, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getpriceDetailsBasedOnbranchIdandIdtypeandtimetypeandactiveStatus,
    "floorId=False, branchId=False, timetype=True, idType=True, activeStatus=True, parkingOwnerId=True, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getpriceDetailsBasedOnparkingOwnerIdandIdtypeandtimetypeandactiveStatus,
    "floorId=False, branchId=False, timetype=True, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=True, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getpriceDetailsBasedOnuserIdandIdtypeandtimetypeandactiveStatus,
    "floorId=False, branchId=False, timetype=True, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=True, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getpriceDetailsBasedOnblockIdandIdtypeandtimetypeandactiveStatus,
    "floorId=False, branchId=False, timetype=True, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getpriceDetailsIdtypeandtimetypeandactiveStatus,
    "floorId=False, branchId=True, timetype=False, idType=True, activeStatus=False, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getpriceDetailsbasedonbranchIdandIdType,
    "floorId=True, branchId=False, timetype=False, idType=False, activeStatus=False, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnFloorId,
    "floorId=True, branchId=False, timetype=False, idType=False, activeStatus=False, parkingOwnerId=False, taxId=False, userMode=True, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnFloorIdUserMode,
    "floorId=False, branchId=True, timetype=False, idType=False, activeStatus=False, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnBranchId,
    "floorId=False, branchId=False, timetype=False, idType=False, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnActiveStatus,
    "floorId=False, branchId=False, timetype=False, idType=False, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=False, priceId=True, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnPriceIdActiveStatus,
    "floorId=False, branchId=True, timetype=False, idType=False, activeStatus=True, parkingOwnerId=True, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnBranchParkingOwnerActiveId,
    "floorId=True, branchId=False, timetype=True, idType=False, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnFloorTimeTypeActiveId,
    "floorId=True, branchId=False, timetype=True, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=True, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnFloorTimeIdTypeActiveUserMode,
    "floorId=True, branchId=False, timetype=True, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=True, priceId=False, vehicleAccessories=True, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnFloorTimeIdTypeActiveUserModeVehicleAccessories,
    "floorId=True, branchId=False, timetype=True, idType=False, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=True, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnFloorTimeTypeActiveUserMode,
    "floorId=True, branchId=False, timetype=False, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=True, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnFloorIdTypeActiveUserMode,
    "floorId=True, branchId=False, timetype=False, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnFloorIdTypeActiveId,
    "floorId=False, branchId=False, timetype=False, idType=False, activeStatus=False, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=True, configTypeId=False, vehicleConfigId=False, type=False":getPriceIdsDetails,
    "floorId=True, branchId=False, timetype=False, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=True, priceId=False, vehicleAccessories=True, userId=False, blockId=False, priceIds=True, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnActiveStatusFloorIdUsermodeIdTypeVehicleAccessories,
    "floorId=True, branchId=False, timetype=False, idType=True, activeStatus=False, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=False":getPriceDetailsBasedOnFloorIdIdType,
    "floorId=True, branchId=False, timetype=False, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=True, vehicleConfigId=False, type=False":getPriceDetailsBasedOnActiveStatusFloorIdIdTypeConfigTypeId,
    "floorId=True, branchId=False, timetype=False, idType=True, activeStatus=True, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=True, type=False":getPriceDetailsBasedOnActiveStatusFloorIdIdTypeVehicleConfigId,
    "floorId=True, branchId=False, timetype=False, idType=True, activeStatus=False, parkingOwnerId=False, taxId=False, userMode=False, priceId=False, vehicleAccessories=False, userId=False, blockId=False, priceIds=False, configTypeId=False, vehicleConfigId=False, type=True":getPriceDetailsBasedOnFloorIdIdTypeType
    
}

##################################################################################################################
@router.get('')
async def pricemasterGet(floorId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),timetype:Optional[str]=Query(None),idType:Optional[str]=Query(None),activeStatus:Optional[str]=Query(None),parkingOwnerId:Optional[int]=Query(None), taxId:Optional[int]=Query(None), userMode:Optional[str]=Query(None), priceId:Optional[int]=Query(None), vehicleAccessories:Optional[int]=Query(None), userId:Optional[int]=Query(None), blockId:Optional[int]=Query(None), priceIds:Optional[List]=Query(None), configTypeId:Optional[int]=Query(None), vehicleConfigId:Optional[int]=Query(None), type:Optional[str]=Query(None), db:Cursor = Depends(get_cursor)):
    try:
        st = f"floorId={True if floorId else False}, branchId={True if branchId else False}, timetype={True if timetype else False}, idType={True if idType else False}, activeStatus={True if activeStatus else False}, parkingOwnerId={True if parkingOwnerId else False}, taxId={True if taxId else False}, userMode={True if userMode else False}, priceId={True if priceId else False}, vehicleAccessories={True if vehicleAccessories else False}, userId={True if userId else False}, blockId={True if blockId else False}, priceIds={True if priceIds else False}, configTypeId={True if configTypeId else False}, vehicleConfigId={True if vehicleConfigId else False}, type={True if type else False}"
        return await priceMasterDict[st](floorId,branchId,timetype,idType,activeStatus,parkingOwnerId,taxId,userMode,priceId,vehicleAccessories,userId,blockId,priceIds,configTypeId,vehicleConfigId,type,db)

    except Exception as e:
        print("Exception as pricemasterGet ",str(e))
        return {
            "response":"Server Error",
            "statusCode": 0
        }

@router.post('')
async def postPriceMaster(request:schemas.PriceMaster,db:Cursor = Depends(get_cursor)):
    try:
        if request.idType=='A':
            configDetails=await getConfigTypeName(request.vehicle_accessories)
 
        if request.idType=='A':
            vehicle_accessoriesNames=redis_client.hget('configMaster',request.vehicle_accessories)
            vehicle_accessoriesName=vehicle_accessoriesNames.decode("utf-8") if vehicle_accessoriesNames else None
        else:
            vehicle_accessoriesNames=redis_client.hget('vehicleConfigMaster',request.vehicle_accessories)
            vehicle_accessoriesName,vehicleImageUrl=tuple(json.loads(vehicle_accessoriesNames.decode("utf-8")).values()) if vehicle_accessoriesNames else None
        
        taxPercentage=await getPriceTaxId(request.taxId)
        
        tax=((request.totalAmount * taxPercentage['taxPercentage']) / 100)
        parkingName = redis_client.hget('parkingOwnerMaster', request.parkingOwnerId)
        branchName = redis_client.hget('branchMaster', request.branchId)
        floorName = redis_client.hget('floorMaster', request.floorId)
        
        
        parkingName=parkingName.decode("utf-8") if parkingName else None
        branchName=branchName.decode("utf-8")  if branchName else None
        floorName=floorName.decode("utf-8")  if floorName else None
        await db.execute(f"""EXEC [dbo].[postPriceMaster]
                                                @parkingOwnerId=?,
                                                @parkingName=?,
                                                @branchId=?,
                                                @branchName=?,
                                                @floorId=?,
                                                @floorName=?,
                                                @totalAmount=?,
                                                @tax=?,
                                                @idType=?,
                                                @vehicle_accessories=?,
                                                @vehicle_accessoriesName=?,
                                                @timeType=?,
                                                @taxId=?,
                                                @taxName=?,
                                                @userMode=?,
                                                @activeStatus=?,
                                                @remarks=?,
                                                @graceTime=?,
                                                @createdBy=?,
                                                @configTypeId=?,
                                                @configTypeName=?
                                                
                                                """,
                                            (request.parkingOwnerId,
                                            parkingName,
                                            request.branchId,
                                            branchName,
                                            request.floorId,
                                            floorName,
                                            request.totalAmount,
                                            tax,
                                            request.idType,
                                            request.vehicle_accessories,
                                            vehicle_accessoriesName,
                                            request.timeType,
                                            request.taxId,
                                            taxPercentage['taxName'],
                                            request.userMode,
                                            request.activeStatus,
                                            request.remarks,
                                            request.graceTime,
                                            request.createdBy,
                                            configDetails['configTypeId'] if configDetails else 0,
                                            configDetails['configTypeName'] if configDetails else None,
                                            ))
        row=await db.fetchall()
        await db.commit()
        return{"statusCode":int(row[0][1]),"response":row[0][0]}

    except Exception as e:
        print("Exception as postPriceMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@router.put('')
async def putPriceMaster(request:schemas.PutPriceMaster,db:Cursor = Depends(get_cursor)):
    try:
        taxPercentage=await getPriceTaxId(request.taxId)
        tax=((request.totalAmount * taxPercentage['taxPercentage']) / 100)
        await db.execute(f"""EXEC [dbo].[putPriceMaster]
                                                @totalAmount =?,
                                                @tax=?,
                                                @idType =?,
                                                @taxId =?,
                                                @taxName=?,
                                                @userMode=?,
                                                @graceTime=?,
                                                @priceId=?,
                                                @updatedBy =?
                                                
                                                """,
                                            (
                                            request.totalAmount,
                                            tax,
                                            request.idType,
                                            request.taxId,
                                            taxPercentage['taxName'],
                                            request.userMode,
                                            request.graceTime,
                                            request.priceId,
                                            request.updatedBy
                                            ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putPriceMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@router.delete('')
async def deletePriceMaster(activeStatus:str,priceId:int,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE priceMaster SET activeStatus=? WHERE priceId=?",activeStatus,priceId)
        await db.commit()
        if result.rowcount>=1:
            if activeStatus=='D':
                return {
                         "statusCode": 1,
                         "response": "Deactivated Successfully"}
            else:
                return {"statusCode": 1,
                        "response": "Activated Successfully"}
        else:
            return { "statusCode": 0,
                    "response": "Data Not Found"}

    except Exception as e:
        print("Exception as deletePriceMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}