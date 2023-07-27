from fastapi import Query
from fastapi.routing import APIRouter
from typing import Optional
from routers.config import get_cursor,redis_client
from fastapi import Depends
from aioodbc.cursor import Cursor
import json,os
import routers
import asyncio
from dotenv import load_dotenv
import schemas
from joblib import Parallel, delayed

load_dotenv()

router = APIRouter(prefix='/floorVehicleMaster',tags=['floorVehicleMaster'])
def callFunction(i):
    return i.dict()

async def floorVehicleDetailsBasedOnBranchId(branchId,vehicleType,floorVehicleId,floorId,capacity,activeStatus, db):
    try:        
        await db.execute(f"""SELECT CAST((select fvm.*,fm.branchName,fm.floorConfigName as floorName from floorVehicleMaster as fvm
                    inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.branchId=?
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
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def floorVehicleDetailsBasedOnFloorVehicleId(branchId,vehicleType,floorVehicleId,floorId,capacity,activeStatus,db):
    try:        
        await db.execute(f"""SELECT CAST((select fvm.*,fm.branchName,fm.floorConfigName as floorName from floorVehicleMaster as fvm
                    inner join floorMaster as fm on fm.floorId=fvm.floorId where fvm.floorVehicleId=?
                    FOR JSON PATH) AS VARCHAR(MAX))""",(floorVehicleId))
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
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def floorVehicleDetailsBasedOnFloorId(branchId,vehicleType,floorVehicleId,floorId,capacity,activeStatus, db):
    try:        
        await db.execute(f"""SELECT CAST((select fvm.*,fm.branchName,fm.floorConfigName as floorName from floorVehicleMaster as fvm
                    inner join floorMaster as fm on fm.floorId=fvm.floorId where fvm.floorId=?
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
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def floorVehicleDetailsBasedOnActiveFloorId(branchId,vehicleType,floorVehicleId,floorId,capacity,activeStatus, db):

    try:        
        await db.execute(f"""SELECT CAST((select fvm.*,fm.branchName,fm.floorConfigName as floorName from floorVehicleMaster as fvm
                    inner join floorMaster as fm on fm.floorId=fvm.floorId where fvm.floorId=? AND fvm.activeStatus=?
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
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def floorVehicleDetailsBasedOnActiveStatus(branchId,vehicleType,floorVehicleId,floorId,capacity,activeStatus, db):
    try:        
        await db.execute(f"""SELECT CAST((select fvm.*,fm.branchName,fm.floorConfigName as floorName from floorVehicleMaster as fvm
                    inner join floorMaster as fm on fm.floorId=fvm.floorId where fvm.activeStatus=?
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
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def floorVehicleDetailsBasedOnvehicleType(branchId,vehicleType,floorVehicleId,floorId,capacity,activeStatus, db):
    data=[]
    try:
        url = f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/branchMaster?activeStatus=A"
        response = await routers.client.get(url)
        var = json.loads(response.text)
        if var['statusCode']==1:
            for id in var['response']:
                await db.execute(f"""SELECT CAST((SELECT fvm.*,fm.branchId,fm.branchName 
                                    FROM floorVehicleMaster AS fvm
                                    INNER JOIN floorMaster AS fm
                                    ON fvm.floorId=fm.floorId AND fm.branchId=?
                                    WHERE fvm.vehicleType=?
                                    FOR JSON PATH) AS VARCHAR(MAX))""",id['branchId'],(vehicleType))
                row = await db.fetchone()
                if row[0] != None:          
                    data.append(json.loads(row[0])[0])
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
        print("Exception as floorVehicleDetailsBasedOnvehicleType ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def floorVehicleDetailsBasedOnCapacity(branchId,vehicleType,floorVehicleId,floorId,capacity,activeStatus, db):
    try:        
        await db.execute(f"""SELECT CAST((select fvm.*,fm.branchName,fm.floorConfigName as floorName,fm.floorName from floorVehicleMaster as fvm
                    inner join floorMaster as fm on fm.floorId=fvm.floorId where fvm.capacity=?
                    FOR JSON PATH) AS VARCHAR(MAX))""",(capacity))

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
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def floorVehicleDetailsBasedOnBranchIdAndActiveStatus(branchId,vehicleType,floorVehicleId,floorId,capacity,activeStatus, db):
    try:        
        await db.execute(f"""SELECT CAST((select DISTINCT (fvm.vehicleTypeName)As vehicleName,ISNULL(SUM(fvm.capacity),0) AS capacity
                     from floorVehicleMaster as fvm
                    inner join floorMaster as fm on fm.floorId=fvm.floorId where fm.branchId=? AND fvm.activeStatus=?
                    GROUP BY fvm.vehicleTypeName,fvm.capacity
                    FOR JSON PATH) AS VARCHAR(MAX))""",(branchId,activeStatus))

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
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def allDetails(branchId,vehicleType,floorVehicleId,floorId,capacity,activeStatus,db):
    try:        
        await db.execute(f"""SELECT CAST((select fvm.*,fm.branchName,fm.floorConfigName as floorName from floorVehicleMaster as fvm
                    inner join floorMaster as fm on fm.floorId=fvm.floorId
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
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


async def floorVehicleDetailsBasedOnBranchIdVehicleType(branchId,vehicleType,floorVehicleId,floorId,capacity,activeStatus,db):
    try:     
          
        await db.execute(f"""SELECT CAST((SELECT ISNULL(SUM(fvm.capacity),0) AS capacity
                                            FROM floorVehicleMaster as fvm
											INNER JOIN floorMaster as fm ON fm.floorId = fvm.floorId
											WHERE fvm.vehicleType = ? AND fm.branchId = ?
                    FOR JSON PATH) AS VARCHAR(MAX))""",vehicleType,branchId)
        row = await db.fetchone()
        
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
        print("Exception as floorVehicleDetailsBasedOnBranchIdVehicleType ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

floorVehicleDict = {
    "branchId=True, vehicleType=False, floorVehicleId=False, floorId=False, capacity=False, activeStatus=False":floorVehicleDetailsBasedOnBranchId,
    "branchId=False, vehicleType=True, floorVehicleId=False, floorId=False, capacity=False, activeStatus=False":floorVehicleDetailsBasedOnvehicleType,
    "branchId=False, vehicleType=False, floorVehicleId=True, floorId=False, capacity=False, activeStatus=False":floorVehicleDetailsBasedOnFloorVehicleId,
    "branchId=False, vehicleType=False, floorVehicleId=False, floorId=True, capacity=False, activeStatus=False":floorVehicleDetailsBasedOnFloorId,
    "branchId=False, vehicleType=False, floorVehicleId=False, floorId=True, capacity=False, activeStatus=True":floorVehicleDetailsBasedOnActiveFloorId,
    "branchId=False, vehicleType=False, floorVehicleId=False, floorId=False, capacity=True, activeStatus=False":floorVehicleDetailsBasedOnCapacity,
    "branchId=False, vehicleType=False, floorVehicleId=False, floorId=False, capacity=False, activeStatus=True":floorVehicleDetailsBasedOnActiveStatus,
    "branchId=True, vehicleType=False, floorVehicleId=False, floorId=False, capacity=False, activeStatus=True":floorVehicleDetailsBasedOnBranchIdAndActiveStatus,
    "branchId=True, vehicleType=True, floorVehicleId=False, floorId=False, capacity=False, activeStatus=False":floorVehicleDetailsBasedOnBranchIdVehicleType,
    "branchId=False, vehicleType=False, floorVehicleId=False, floorId=False, capacity=False, activeStatus=False":allDetails
}

##################################################################################################################
@router.get('')
async def floorVehicleGet(floorVehicleId:Optional[int]=Query(None),floorId:Optional[int]=Query(None),capacity:Optional[int]=Query(None),branchId:Optional[int]=Query(None),vehicleType:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None), db:Cursor = Depends(get_cursor)):
    try:
        st = f"branchId={True if branchId else False}, vehicleType={True if vehicleType else False}, floorVehicleId={True if floorVehicleId else False}, floorId={True if floorId else False}, capacity={True if capacity else False}, activeStatus={True if activeStatus else False}"
        return await floorVehicleDict[st](branchId,vehicleType,floorVehicleId,floorId,capacity,activeStatus, db)
    except Exception as e:
        print("Exception as floorVehicleGet ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@router.post('')
async def postfloorVehicleMaster(request:schemas.PostfloorVehicleMaster,db:Cursor = Depends(get_cursor)):
    try:
        vehicleDetails=redis_client.hget('vehicleConfigMaster',request.vehicleType)
      
        data=json.loads(vehicleDetails.decode("utf-8")) if vehicleDetails else None
        if data !=None:
            await db.execute(f"""
                            EXEC [dbo].[postfloorVehicleMaster] 
                            @floorId=?,
                            @vehicleType=?,
                            @vehicleTypeName=?,
                            @vehicleImageUrl=?,
                            @vehiclePlaceHolderImageUrl=?,
                            @capacity=?,
                            @length=?,
                            @height=?,
                            @rules=?,
                            @activeStatus=?,
                            @createdBy=?
                            """,
                            (request.floorId,
                            request.vehicleType,
                            data['vehicleTypeName'],
                            data['vehicleImageUrl'],
                            data['vehiclePlaceHolderImageUrl'],
                            request.capacity,
                            request.length,
                            request.height,
                            request.rules,
                            request.activeStatus,
                            request.createdBy
                        ))
            row=await db.fetchone()
            await db.commit()
            return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postfloorVehicleMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}
    
    
@router.put('')
async def putfloorVehicleMaster(request:schemas.PutfloorVehicleMaster,db:Cursor = Depends(get_cursor)):
    try:
        vehicleDetails=redis_client.hget('vehicleConfigMaster',request.vehicleType)
      
        data=json.loads(vehicleDetails.decode("utf-8")) if vehicleDetails else None
        if data !=None:
            await db.execute("""
                                EXEC [dbo].[putfloorVehicleMaster] 
                                @floorId=?,
                                @floorVehicleId=?,
                                @vehicleType=?,
                                @vehicleTypeName=?,
                                @vehicleImageUrl=?,
                                @vehiclePlaceHolderImageUrl=?,
                                @capacity=?,
                                @length=?,
                                @height=?,
                                @rules=?,
                                @updatedBy=?
                                """,
                                    (
                                    request.floorId,
                                    request.floorVehicleId,
                                    request.vehicleType,
                                    data['vehicleTypeName'],
                                    data['vehicleImageUrl'],
                                    data['vehiclePlaceHolderImageUrl'],
                                    request.capacity,
                                    request.length,
                                    request.height,
                                    request.rules,
                                    request.updatedBy
                                    ))
            row=await db.fetchone()
            await db.commit()
            return{"statusCode":int(row[1]),"response":row[0]}
    
    except Exception as e:
        print("Exception as putfloorVehicleMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}
    
    
@router.delete('')    
async def deletefloorVehicleMaster(floorVehicleId:int,activeStatus:str,db:Cursor = Depends(get_cursor)):
    try:
        if activeStatus == 'A':
            data=await db.execute(f"""
                        DECLARE @floorId INT,
                        @vehicleType INT ,
                        @floorVehicleId INT = ?

                        SELECT @floorId = floorId, @vehicleType = vehicleType FROM floorVehicleMaster
                        WHERE floorVehicleId= @floorVehicleId

                        SELECT * FROM floorVehicleMaster
                        WHERE floorId = @floorId AND vehicleType =@vehicleType AND floorVehicleId != @floorVehicleId AND activeStatus = 'A'
               """, (floorVehicleId))
            row = data.fetchone()
            if row[0] != None:
                return {
                    "statusCode":0,
                    "response": "Data Already Exists"
                }

            
        result=await db.execute("UPDATE floorVehicleMaster SET activeStatus=? WHERE floorVehicleId=?",activeStatus,floorVehicleId)
        await db.commit()
        if result.rowcount>=1:
            if activeStatus=='A':
                return {
                            "statusCode": 1,
                            "response": "Data Activated Successfully"
                        }
            else:
                return {
                            "statusCode": 1,
                            "response": "Data Inactivated Successfully"
                        }
        else:
            return { "statusCode": 0,
                    "response": "Data Not Found"
                }
    
    
    except Exception as e:
        print("Exception as deletefloorVehicleMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}
    
