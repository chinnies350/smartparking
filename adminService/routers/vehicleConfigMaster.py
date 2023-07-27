import json
from sqlite3 import Cursor
from fastapi.routing import APIRouter
from routers.config import get_cursor
from fastapi import Depends
from typing import Optional
from fastapi import Query
import schemas,os,routers
from routers import Response
from task import postVehicleName


vehicleConfigRouter = APIRouter(prefix='/vehicleConfigMaster')

async def getfloorVehicleConfigIdBasedOnFloorId(floorId):
    try:
        
        url=f"{os.getenv('SLOT_SERVICE_URL')}/floorVehicleMaster?floorId={floorId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getfloorVehicleConfigIdBasedOnFloorId ",str(e))
        return ""

async def getfloorVehicleConfigIdBasedOnBranchId(branchId):
    try:
        
        url=f"{os.getenv('SLOT_SERVICE_URL')}/floorVehicleMaster?branchId={branchId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getfloorVehicleConfigIdBasedOnBranchId ",str(e))
        return ""

@vehicleConfigRouter.get('')
async def getVehicleConfigMaster(vehicleConfigId:Optional[int]=Query(None),vehicleName:Optional[str]=Query(None),activeStatus:Optional[str]=Query(None), floorId:Optional[int]=Query(None), type:Optional[str]=Query(None),branchId:Optional[int]=Query(None),db: Cursor = Depends(get_cursor)):
    try:
        
        if floorId:
            floorVehicleConfigId=await getfloorVehicleConfigIdBasedOnFloorId(floorId)
            
            if floorVehicleConfigId!="":
                await db.execute(f"""SELECT CAST((SELECT * 
                                                    FROM vehicleConfigMasterView
                                                    WHERE activeStatus='A' and vehicleConfigId NOT IN {(tuple(i['vehicleType'] for i in floorVehicleConfigId)+tuple('0'))}
                                FOR JSON PATH) AS VARCHAR(MAX))""")
            else:
                return Response("NotFound")
        elif branchId:
            branchVehicleConfigId=await getfloorVehicleConfigIdBasedOnBranchId(branchId)
            
            if branchVehicleConfigId!="":
                await db.execute(f"""SELECT CAST((SELECT * 
                                                    FROM vehicleConfigMasterView
                                                    WHERE activeStatus='A' and vehicleConfigId IN {(tuple(i['vehicleType'] for i in branchVehicleConfigId)+tuple('0'))}
                                FOR JSON PATH) AS VARCHAR(MAX))""")
            else:
                return Response("NotFound")
        else:
            await db.execute(f"""EXEC [dbo].[getvehicleConfigMaster]?,?,?,?""",vehicleConfigId,vehicleName,activeStatus,type)
        rows=await db.fetchone()
        
        if rows[0]:
            return {"statusCode": 1,"response":json.loads(rows[0]) if rows[0] != None else []}
        else:
            return Response("NotFound")           
    except Exception as e:
        print("Exception as getVehicleConfigMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@vehicleConfigRouter.post('')
async def postVehicleConfigMaster(request:schemas.VehicleConfigMaster,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postvehicleConfigMaster]
                                    @vehicleName=?,
                                    @vehicleImageUrl=?,
                                    @vehiclePlaceHolderImageUrl=?,
                                    @vehicleKeyName=?,
                                    @activeStatus=?,
                                    @createdBy=?""",
                                    (request.vehicleName,
                                    request.vehicleImageUrl,
                                    request.vehiclePlaceHolderImageUrl,
                                    request.vehicleKeyName,
                                    request.activeStatus,
                                    request.createdBy))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            postVehicleName.delay(int(row[2]),request.vehicleName,request.vehicleImageUrl,request.vehiclePlaceHolderImageUrl)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postVehicleConfigMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@vehicleConfigRouter.put('')
async def putVehicleConfigMaster(request:schemas.PutVehicleConfigMaster,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putvehicleConfigMaster]
                                   @vehicleName=?,
                                   @vehicleImageUrl=?,
                                   @vehiclePlaceHolderImageUrl=?,
                                   @vehicleKeyName=?,
                                   @updatedBy=?,
                                   @vehicleConfigId=?""",
                                   (request.vehicleName,
                                   request.vehicleImageUrl,
                                   request.vehiclePlaceHolderImageUrl,
                                   request.vehicleKeyName,
                                   request.updatedBy,
                                   request.vehicleConfigId))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            postVehicleName.delay(request.vehicleConfigId,request.vehicleName,request.vehicleImageUrl,request.vehiclePlaceHolderImageUrl)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putVehicleConfigMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}



@vehicleConfigRouter.delete('')
async def deleteVehicleConfigMaster(vehicleConfigId:int,activeStatus:str,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE vehicleConfigMaster SET activeStatus=? WHERE vehicleConfigId=?",activeStatus,vehicleConfigId)
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
                    "response": "Data Not Deleted"}

    except Exception as e:
        print("Exception as deleteVehicleConfigMaster ",str(e))
        return{"stausCode":0, "response":"Server Error"}