from fastapi import Query
from fastapi.routing import APIRouter
from typing import Optional
from routers.config import get_cursor,redis_client
from fastapi import Depends
from aioodbc.cursor import Cursor
import json
import schemas
import routers
import asyncio
import os
from dotenv import load_dotenv
load_dotenv()

parkingPassConfigRouter = APIRouter(prefix='/parkingPassConfig',tags=['parkingPassConfig'])

async def getParkingPassConfigTaxId(taxId):
    try:
        response = await routers.client.get(f"{os.getenv('ADMIN_SERVICE_URL')}/taxMaster?taxId={taxId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response'][0]
        return None
    except Exception as e:
        print("Exception as getParkingPassConfigTaxId ",str(e))
        return None
        
async def getNameDetails(taxId,totalAmount,parkingOwnerId,branchId,vehicleType):
    try:
        taxPercentage=await getParkingPassConfigTaxId(taxId)
        if taxPercentage:
            tax=((totalAmount * taxPercentage.get('taxPercentage')) / 100)
            taxName=taxPercentage.get('taxName')
            taxPercentage=taxPercentage.get('taxPercentage')
        else:
            tax=0
            taxPercentage=0
            taxName=None
        parkingName = redis_client.hget('parkingOwnerMaster', parkingOwnerId)
        branchName = redis_client.hget('branchMaster', branchId)
        vehicleDetails=redis_client.hget('vehicleConfigMaster',vehicleType)
        vehicleTypeName,vehicleImageUrl=tuple(json.loads(vehicleDetails.decode("utf-8")).values()) if vehicleDetails else None
        parkingName=parkingName.decode("utf-8") if parkingName else None
        branchName=branchName.decode("utf-8") if branchName else None
        return tax,taxName,taxPercentage,parkingName,branchName,vehicleTypeName,vehicleImageUrl

    except Exception as e:
        print("Exception as getNameDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }  

async def parkingPassActiveDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType,type,db):
    try:
        await db.execute(f"""SELECT CAST((SELECT DISTINCT pc.branchId FROM  parkingPassConfig as pc
                                WHERE pc.activeStatus=?
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
        print("Exception as parkingPassActiveDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
async def parkingPassConfigIdDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.parkingPassConfigId = ?  FOR JSON PATH) AS  varchar(max))""", (parkingPassConfigId))
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
        print("Exception as parkingPassConfigIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def parkingOwnerIdDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.parkingOwnerId = ?  FOR JSON PATH) AS  varchar(max))""", (parkingOwnerId))
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
        print("Exception as parkingOwnerIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def parkingBranchIdDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.branchId = ?  FOR JSON PATH) AS  varchar(max))""", (branchId))
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
        print("Exception as parkingBranchIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            }
async def parkingTaxIdDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.taxId = ?  FOR JSON PATH) AS  varchar(max))""", (taxId))
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
        print("Exception as parkingTaxIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def parkingPassConfigTaxIdTypeDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        # type-T means taxMaxDate calculation
        await db.execute(f"""SELECT CAST(MAX(ppc.createdDate) as date)AS parkingPassConfig
                                FROM parkingPassConfig AS ppc
                                WHERE ppc.taxId = ?
                                """, (taxId))
        row = await db.fetchone()
        if row[0] != None:           
            return {
            "response":row[0],
            "statusCode":1
        }                
        return {
            "response":"data not found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as parkingPassConfigTaxIdTypeDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
async def parkingVehicleTypeDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.vehicleType = ?  FOR JSON PATH) AS  varchar(max))""", (vehicleType))
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
        print("Exception as parkingVehicleTypeDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
async def parkingBranchVehicleTypeDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.vehicleType = ? AND pc.branchId=?  FOR JSON PATH) AS  varchar(max))""", (vehicleType,branchId))
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
        print("Exception as parkingBranchVehicleTypeDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def parkingBranchVehicleTypeActiveDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.vehicleType = ? AND pc.branchId=? AND pc.activeStatus=?  FOR JSON PATH) AS  varchar(max))""", (vehicleType,branchId,activeStatus))
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
        print("Exception as parkingBranchVehicleTypeActiveDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def parkingBranchVehicleTypePassCActiveDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.vehicleType = ? AND pc.branchId=? AND pc.activeStatus=? AND pc.passCategory=?  FOR JSON PATH) AS  varchar(max))""", (vehicleType,branchId,activeStatus,passCategory))
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
        print("Exception as parkingBranchVehicleTypePassCActiveDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def parkingBranchVehicleTypePassCTActiveDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.vehicleType = ? AND pc.branchId=? AND pc.activeStatus=? AND pc.passCategory=? AND pc.passType=?  FOR JSON PATH) AS  varchar(max))""", (vehicleType,branchId,activeStatus,passCategory,passType))
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
        print("Exception as parkingBranchVehicleTypePassCTActiveDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
async def parkingPassCategoryDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.passCategory = ?  FOR JSON PATH) AS  varchar(max))""", (passCategory))
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
        print("Exception as parkingPassCategoryDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def parkingPassCategoryActiveDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.passCategory = ? AND pc.activeStatus=?  FOR JSON PATH) AS  varchar(max))""", (passCategory,activeStatus))
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
        print("Exception as parkingPassCategoryActiveDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def parkingPassCategoryTypeDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.passCategory = ? AND pc.passType=?  FOR JSON PATH) AS  varchar(max))""", (passCategory,passType))
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
        print("Exception as parkingPassCategoryTypeDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }   
async def parkingPassCategoryVehicleTypeDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                WHERE pc.passCategory = ? AND pc.passType=? AND pc.vehicleType=?  FOR JSON PATH) AS  varchar(max))""", (passCategory,passType,vehicleType))
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
        print("Exception as parkingPassCategoryVehicleTypeDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        } 
async def parkingPassConfigDetails(activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pc.* FROM parkingPassConfig AS pc
                                                  FOR JSON PATH) AS  varchar(max))""")
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
        print("Exception as parkingPassConfigDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }  

parkingPassDict = {
   "activeStatus=True, parkingPassConfigId=False, parkingOwnerId=False, branchId=False, passCategory=False, passType=False, taxId=False, vehicleType=False, type=False":parkingPassActiveDetails,
   "activeStatus=False, parkingPassConfigId=True, parkingOwnerId=False, branchId=False, passCategory=False, passType=False, taxId=False, vehicleType=False, type=False":parkingPassConfigIdDetails,
   "activeStatus=False, parkingPassConfigId=False, parkingOwnerId=True, branchId=False, passCategory=False, passType=False, taxId=False, vehicleType=False, type=False":parkingOwnerIdDetails,
   "activeStatus=False, parkingPassConfigId=False, parkingOwnerId=False, branchId=True, passCategory=False, passType=False, taxId=False, vehicleType=False, type=False":parkingBranchIdDetails,
   "activeStatus=False, parkingPassConfigId=False, parkingOwnerId=False, branchId=False, passCategory=False, passType=False, taxId=True, vehicleType=False, type=False":parkingTaxIdDetails,
   "activeStatus=False, parkingPassConfigId=False, parkingOwnerId=False, branchId=False, passCategory=False, passType=False, taxId=False, vehicleType=True, type=False":parkingVehicleTypeDetails,
   "activeStatus=False, parkingPassConfigId=False, parkingOwnerId=False, branchId=True, passCategory=False, passType=False, taxId=False, vehicleType=True, type=False":parkingBranchVehicleTypeDetails,
   "activeStatus=False, parkingPassConfigId=False, parkingOwnerId=False, branchId=False, passCategory=True, passType=False, taxId=False, vehicleType=False, type=False":parkingPassCategoryDetails,
   "activeStatus=False, parkingPassConfigId=False, parkingOwnerId=False, branchId=False, passCategory=True, passType=True, taxId=False, vehicleType=False, type=False":parkingPassCategoryTypeDetails,
   "activeStatus=False, parkingPassConfigId=False, parkingOwnerId=False, branchId=False, passCategory=True, passType=True, taxId=False, vehicleType=True, type=False":parkingPassCategoryVehicleTypeDetails,
   "activeStatus=False, parkingPassConfigId=False, parkingOwnerId=False, branchId=False, passCategory=False, passType=False, taxId=False, vehicleType=False, type=False":parkingPassConfigDetails,
   "activeStatus=False, parkingPassConfigId=False, parkingOwnerId=False, branchId=False, passCategory=False, passType=False, taxId=True, vehicleType=False, type=True":parkingPassConfigTaxIdTypeDetails,
   "activeStatus=True, parkingPassConfigId=False, parkingOwnerId=False, branchId=True, passCategory=False, passType=False, taxId=False, vehicleType=True, type=False":parkingBranchVehicleTypeActiveDetails,
   "activeStatus=True, parkingPassConfigId=False, parkingOwnerId=False, branchId=True, passCategory=True, passType=False, taxId=False, vehicleType=True, type=False":parkingBranchVehicleTypePassCActiveDetails,
   "activeStatus=True, parkingPassConfigId=False, parkingOwnerId=False, branchId=True, passCategory=True, passType=True, taxId=False, vehicleType=True, type=False":parkingBranchVehicleTypePassCTActiveDetails,
   "activeStatus=True, parkingPassConfigId=False, parkingOwnerId=False, branchId=False, passCategory=True, passType=False, taxId=False, vehicleType=False, type=False":parkingPassCategoryActiveDetails
}

##################################################################################################################
@parkingPassConfigRouter.get('')
async def parkingPassConfig(activeStatus:Optional[str]=Query(None),parkingPassConfigId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),passCategory:Optional[str]=Query(None),passType:Optional[str]=Query(None),taxId:Optional[int]=Query(None),vehicleType:Optional[int]=Query(None),type:Optional[str]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"activeStatus={True if activeStatus else False}, parkingPassConfigId={True if parkingPassConfigId else False}, parkingOwnerId={True if parkingOwnerId else False}, branchId={True if branchId else False}, passCategory={True if passCategory else False}, passType={True if passType else False}, taxId={True if taxId else False}, vehicleType={True if vehicleType else False}, type={True if type else False}"
        return await parkingPassDict[st](activeStatus,parkingPassConfigId, parkingOwnerId, branchId, passCategory, passType, taxId, vehicleType, type,db)
    except Exception as e:
        print("Exception as parkingPassConfig ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        } 

@parkingPassConfigRouter.post('')
async def postParkingPassConfig(request:schemas.ParkingPassConfig,db:Cursor = Depends(get_cursor)):
    try:
        
        tax,taxName,taxPercentage,parkingName,branchName,vehicleTypeName,vehicleImageUrl=await getNameDetails(request.taxId,request.totalAmount,request.parkingOwnerId,request.branchId,request.vehicleType)
        await db.execute(f"""EXEC [dbo].[postParkingPassConfig]
                                    @parkingOwnerId=?,
                                    @parkingName=?,
                                    @branchId=?,
                                    @branchname=?,
                                    @passCategory=?,
                                    @passType=?,
                                    @noOfDays=?,
                                    @parkingLimit=?,
                                    @tax=?,
                                    @taxId=?,
                                    @taxName=?,
                                    @taxPercentage=?,
                                    @vehicleType=?,
                                    @vehicleTypeName=?,
                                    @vehicleImageUrl=?,
                                    @totalAmount=?,
                                    @remarks=?,
                                    @activeStatus=?,
                                    @createdBy=?
                                    """,
                                    (request.parkingOwnerId,
                                    parkingName,
                                    request.branchId,
                                    branchName,
                                    request.passCategory,
                                    request.passType,
                                    request.noOfDays,
                                    request.parkingLimit,
                                    tax,
                                    request.taxId,
                                    taxName,
                                    taxPercentage,
                                    request.vehicleType,
                                    vehicleTypeName,
                                    vehicleImageUrl,
                                    request.totalAmount,
                                    request.remarks,
                                    request.activeStatus,
                                    request.createdBy))
        row=await db.fetchone()
        
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}     

    except Exception as e:
        print("Exception as postparkingPassConfig ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@parkingPassConfigRouter.put('')
async def putParkingPassConfig(request:schemas.PutParkingPassConfig,db:Cursor = Depends(get_cursor)):
    try:
        tax,taxName,taxPercentage,parkingName,branchName,vehicleTypeName,vehicleImageUrl=await getNameDetails(request.taxId,request.totalAmount,request.parkingOwnerId,request.branchId,request.vehicleType)
        await db.execute(f"""EXEC [dbo].[putParkingPassConfig]
                                    @passCategory=?,
                                    @passType=?,
                                    @noOfDays=?,
                                    @parkingLimit=?,
                                    @totalAmount=?,
                                    @tax=?,
                                    @taxId=?,
                                    @taxName=?,
                                    @taxPercentage=?,
                                    @vehicleType=?,
                                    @vehicleTypeName=?,
                                    @vehicleImageUrl=?,
                                    @remarks=?,
                                    @activeStatus=?,
                                    @updatedBy=?,
                                    @parkingPassConfigId=?,
                                    @parkingOwnerId=?,
                                    @parkingName=?,
                                    @branchId=?,
                                    @branchName=?""",
                                    (request.passCategory,
                                    request.passType, 
                                    request.noOfDays,
                                    request.parkingLimit,
                                    request.totalAmount,
                                    tax,
                                    request.taxId,
                                    taxName,
                                    taxPercentage,
                                    request.vehicleType,
                                    vehicleTypeName,
                                    vehicleImageUrl,
                                    request.remarks,
                                    request.activeStatus,
                                    request.updatedBy,
                                    request.parkingPassConfigId,
                                    request.parkingOwnerId,
                                    parkingName,
                                    request.branchId,
                                    branchName
                                   ))
        row=await db.fetchone()
        
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}    

    except Exception as e:
        print("Exception as putparkingPassConfig ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@parkingPassConfigRouter.delete('')
async def deleteParkingPassConfig(activeStatus:str,parkingPassConfigId:int,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE parkingPassConfig SET activestatus=? WHERE parkingPassConfigId=?",activeStatus,parkingPassConfigId)
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
        print("Exception as deleteParkingPassConfig ",str(e))
        return{"statusCode":0,"response":"Server Error"}