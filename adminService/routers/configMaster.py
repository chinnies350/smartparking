
from fastapi import Query
from fastapi.routing import APIRouter
from typing import Optional
from routers.config import get_cursor
from fastapi import Depends
from aioodbc.cursor import Cursor
import json
import schemas
import routers
from task import postConfigName
import os
from dotenv import load_dotenv
load_dotenv()

configMasterRouter = APIRouter(prefix='/configMaster',tags=['configMaster'])


async def getFloorName(blockId):
    try:
        response = await routers.client.get(f"{os.getenv('SLOT_SERVICE_URL')}/floorMaster?blockId={blockId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getFloorName ",str(e))
        return ""

async def getDetailsBasedOnConfigId(configId,configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db):
    data =[]
    try:
        await db.execute(f"""SELECT CAST((SELECT * FROM configMasterView
                            WHERE configId=?
                            FOR JSON PATH) AS VARCHAR(MAX))""",(configId))
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
        print("Exception as getDetailsBasedOnConfigId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnConfigTypeId(configId,configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db):
    
    try:
        await db.execute(f"""SELECT CAST((SELECT * FROM configMasterView
                            WHERE configTypeId=?
                            FOR JSON PATH) AS VARCHAR(MAX))""",(configTypeId))
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
        print("Exception as getDetailsBasedOnConfigTypeId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def configDetailsBasedOnActiveStatus(configId,configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db):
    
    try:
        await db.execute(f"""SELECT CAST((SELECT * FROM configMasterView
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
        print("Exception as configDetailsBasedOnActiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
async def getDetailsBasedOnConfigTypeIdActive(configId,configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db):
    
    try:
        await db.execute(f"""SELECT CAST((SELECT * FROM configMasterView
                            WHERE configTypeId=? AND activeStatus=?
                            FOR JSON PATH) AS VARCHAR(MAX))""",(configTypeId,activeStatus))
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
        print("Exception as getDetailsBasedOnConfigTypeIdActive ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnParkingConfigTypeName(configId,configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db):
    
    try:
        await db.execute(f"""SELECT CAST((SELECT * FROM configMasterView
                            WHERE configTypeName=? AND parkingOwnerId=?
                            FOR JSON PATH) AS VARCHAR(MAX))""",(configTypeName,parkingOwnerId))
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
        print("Exception as getDetailsBasedOnParkingConfigTypeName ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnActiveConfigTypeName(configId,configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db):
    
    try:
        await db.execute(f"""SELECT CAST((SELECT a.configId,a.configName,a.configTypeId,a.configTypeName,a.parkingOwnerId,a.activeStatus,b.activeStatus as confiTypeActivestatus
							FROM configMasterView as a
							INNER JOIN configType as b on a.configTypeId=b.configTypeId WHERE b.typeName=? and a.activeStatus=?
							and b.activeStatus=?
                            FOR JSON PATH) AS VARCHAR(MAX))""",(configTypeName,activeStatus,activeStatus))
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
        print("Exception as getDetailsBasedOnActiveConfigTypeName ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnBlockActiveConfigName(configId,configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db):
   
    try:
        floorName=await getFloorName(blockId)
        if floorName!="":
            await db.execute(f"""SELECT CAST((SELECT a.configId,a.configName,a.configTypeId,a.configTypeName,a.parkingOwnerId,a.activeStatus,b.activeStatus as confiTypeActivestatus
                                FROM configMasterView as a
                                inner join configType as b on a.configTypeId=b.configTypeId 
                                WHERE b.typeName=? and a.activeStatus=?
                                and b.activeStatus=? and a.configId not in {(tuple(i['floorNameId'] for i in floorName)+tuple('0'))}
                                FOR JSON PATH) AS VARCHAR(MAX))""",(configTypeName,activeStatus,activeStatus))
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
        print("Exception as getDetailsBasedOnBlockActiveConfigName ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def configDetailsBasedOnConfigName(configId,configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db):
    
    try:
        await db.execute(f"""SELECT CAST((SELECT * FROM configMaster
                            WHERE configName=? 
                            FOR JSON PATH) AS VARCHAR(MAX))""",(configName))
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
        print("Exception as configDetailsBasedOnConfigName ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def configDetailsBasedOnConfigTypeName(configId,configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db):
    
    try:
        await db.execute(f"""SELECT CAST((SELECT configId ,configName
                                        FROM configMaster as cm INNER JOIN configType as ct ON ct.configTypeId = cm.configTypeId 
                                        WHERE ct.typeName=? AND cm.configName NOT IN ('DeActive', 'Blocked', 'Path')
                            FOR JSON PATH) AS VARCHAR(MAX))""",(configTypeName))
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
        print("Exception as configDetailsBasedOnConfigTypeName ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def configDetailsBasedOnConfigTypeNameAndConfigName(configId,configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db):
    
    try:
        await db.execute(f"""SELECT CAST((SELECT configId ,configName
                                        FROM configMaster as cm INNER JOIN configType as ct ON ct.configTypeId = cm.configTypeId 
                                        WHERE ct.typeName=? AND cm.configName=? AND cm.configName NOT IN ('DeActive', 'Blocked', 'Path')
                            FOR JSON PATH) AS VARCHAR(MAX))""",(configTypeName,configName))
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
        print("Exception as configDetailsBasedOnConfigTypeName ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getConfigMasterDetails(configId,configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT cmv.*
                            FROM configMasterView as cmv
                            FOR JSON PATH) AS varchar(max))""")
        row = await db.fetchone()
        if row[0] !=None:
            return {
                "response": json.loads(row[0]),
                "statusCode":1
            }
        
        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as getConfigMasterDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

configDict = {
    "configId=True, configTypeId=False, activeStatus=False, configTypeName=False, parkingOwnerId=False, blockId=False, configName=False":getDetailsBasedOnConfigId,
    "configId=False, configTypeId=True, activeStatus=False, configTypeName=False, parkingOwnerId=False, blockId=False, configName=False":getDetailsBasedOnConfigTypeId,
    "configId=False, configTypeId=False, activeStatus=True, configTypeName=False, parkingOwnerId=False, blockId=False, configName=False":configDetailsBasedOnActiveStatus,
    "configId=False, configTypeId=True, activeStatus=True, configTypeName=False, parkingOwnerId=False, blockId=False, configName=False":getDetailsBasedOnConfigTypeIdActive,
    "configId=False, configTypeId=False, activeStatus=False, configTypeName=True, parkingOwnerId=True, blockId=False, configName=False":getDetailsBasedOnParkingConfigTypeName,
    "configId=False, configTypeId=False, activeStatus=True, configTypeName=True, parkingOwnerId=False, blockId=False, configName=False":getDetailsBasedOnActiveConfigTypeName,
    "configId=False, configTypeId=False, activeStatus=True, configTypeName=True, parkingOwnerId=False, blockId=True, configName=False":getDetailsBasedOnBlockActiveConfigName,
    "configId=False, configTypeId=False, activeStatus=False, configTypeName=False, parkingOwnerId=False, blockId=False, configName=True":configDetailsBasedOnConfigName,
    "configId=False, configTypeId=False, activeStatus=False, configTypeName=True, parkingOwnerId=False, blockId=False, configName=False":configDetailsBasedOnConfigTypeName,
    "configId=False, configTypeId=False, activeStatus=False, configTypeName=True, parkingOwnerId=False, blockId=False, configName=True":configDetailsBasedOnConfigTypeNameAndConfigName,
    "configId=False, configTypeId=False, activeStatus=False, configTypeName=False, parkingOwnerId=False, blockId=False, configName=False":getConfigMasterDetails
}

##################################################################################################################

    
@configMasterRouter.get('')
async def getconfigMaster(configId:Optional[int]=Query(None),configTypeId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),configTypeName:Optional[str]=Query(None),parkingOwnerId:Optional[int]=Query(None),blockId:Optional[int]=Query(None),configName:Optional[str]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        st = f"configId={True if configId else False}, configTypeId={True if configTypeId else False}, activeStatus={True if activeStatus else False}, configTypeName={True if configTypeName else False}, parkingOwnerId={True if parkingOwnerId else False}, blockId={True if blockId else False}, configName={True if configName else False}"
        return await configDict[st](configId, configTypeId, activeStatus, configTypeName, parkingOwnerId, blockId, configName, db)
    except Exception as e:
        print("Exception as getConfigMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}
    # if configId:
    #     return await getDetailsBasedOnconfigId(configId,db)
    # elif activeStatus:
    #     return await configDetailsBasedOnactiveStatus(activeStatus,db)
    # elif configName:
    #     return await configDetailsBasedOnconfigname(configName,db)
    # else:
    #     return await getConfigMasterDetails(db)

@configMasterRouter.post('')
async def postConfigMaster(request:schemas.ConfigMaster,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postConfigMaster]
                                    @parkingOwnerId=?,
                                    @configTypeId=?,
                                    @configName=?,
                                    @activeStatus=?,
                                    @createdBy=?""",
                        (
                            None,
                            request.configTypeId,
                            request.configName,
                            request.activeStatus,
                            request.createdBy   
                        ))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            postConfigName.delay(int(row[2]),request.configName)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postConfigMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@configMasterRouter.put('')
async def putConfigMaster(request:schemas.PutConfigMaster,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putConfigMaster]
                                    @configName=?,
                                    @activeStatus=?,
                                    @updatedBy=?,
                                    @parkingOwnerId=?,
                                    @configTypeId=?,
                                    @configId=?""",
                                                       
                            (request.configName,
                            request.activeStatus,
                            request.updatedBy,  
                            None,        
                            request.configTypeId,
                            request.configId
                        ))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            postConfigName.delay(int(row[2]),request.configName)
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}


    except Exception as e:
        print("Exception as putConfigMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@configMasterRouter.delete('')
async def deleteConfigMaster(activeStatus:str,configId:int,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE ConfigMaster SET activeStatus=? WHERE configId=?",activeStatus,configId)
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
        print("Exception as deleteConfigMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}

# async def configDetailsBasedOnconfigTypeId(activeStatus,db):
#     data =[]
#     try:
#         await db.execute(f"""SELECT CAST((SELECT * FROM configMaster 
#                             WHERE configTypeId IN (SELECT configTypeId FROM configType WHERE typeName IN( 'slotType')) AND configName NOT IN ('Blocked', 'DeActive','Inactive') OR configName IN ('Blocked') AND activeStatus=?
#                             FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus))
#         row = await db.fetchone()
#         if row[0] != None:
#             data=json.loads(row[0])
#             return {
#                 "data":data,
#                 "statusCode":1
#             }
#         return {
#             "data":"data not found",
#             "statusCode":0
#         }
#     except Exception as e:
#         print(f'error {str(e)}')
#         return {
#             "data":str(e),
#             "statusCode":0
#         }

# configDict = {
#     "activeStatus=True":configDetailsBasedOnconfigTypeId
# }

# ##################################################################################################################
# @router.get('')
# async def addressGet(activeStatus:Optional[str]=Query(None), db:Cursor = Depends(get_cursor)):
#     st = f"activeStatus={True if activeStatus else False}"
#     return await configDict[st](activeStatus,db)