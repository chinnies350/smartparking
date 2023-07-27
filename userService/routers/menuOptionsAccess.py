import json
from sqlite3 import Cursor
import routers
from fastapi.routing import APIRouter
from fastapi import Depends
from typing import Optional
from fastapi import Query
import schemas
from routers.config import get_cursor
import os
import asyncio
from joblib import Parallel, delayed
from dotenv import load_dotenv
from datetime import date,time


load_dotenv()

menuOptionAccessRouter = APIRouter(prefix='/menuOptionAccess')

def callFunction(i):
    return i.dict()

async def getMenuOptionAccessOnUserName(userId):
    try:
        response = await routers.client.get(f"{os.getenv('USER_SERVICE_URL')}/userMaster?userId={userId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getMenuOptionAccessOnUserName ",str(e))
        return ""

async def getUserId(branchId):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/employeeMaster?branchId={branchId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getUserId ",str(e))
        return ""

async def getOptionName(optionId):
    try:
        response = await routers.client.get(f"{os.getenv('ADMIN_SERVICE_URL')}/menuOptions?optionId={optionId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getOptionName ",str(e))
        return ""

async def modifiedDataUserName(userId, dic):
    userDetails = await getMenuOptionAccessOnUserName(userId)
    
    if userDetails!="":
        dic['userId']=userDetails[0].get('userId')
        dic['userName']=userDetails[0].get('userName')
        dic['userRole']=userDetails[0].get('userRole')
        dic['floorId']=userDetails[0].get('floorId')
        dic['branchId']=userDetails[0].get('branchId')
        dic['floorName']=userDetails[0].get('floorName')
        dic['branchName']=userDetails[0].get('branchName')
        dic['parkingOwnerId']=userDetails[0].get('parkingOwnerId')
        dic['parkingName']=userDetails[0].get('parkingName')




async def modifiedDataOptionsName(optionId, optionDic):
    optionDetails = await getOptionName(optionId)
    optionDic['optionName']=optionDetails[0]['optionName']
    optionDic['menuOptionActiveStatus']=optionDetails[0]['activeStatus']
    

async def modifiedDataOptionsDetails(userId, dic,dicData,db):
    data = []
    await db.execute(f"""SELECT CAST((SELECT MOP.optionId,MOP.MenuOptionAccessId,(MOP.activeStatus) AS MenuOptionAccessActiveStatus,
											( CASE 
												WHEN MOP.AddRights=1 THEN 'True'
											ELSE 'False'
											END) AS AddRights ,
                                            ( CASE 
                                                WHEN MOP.EditRights=1 THEN 'True'
                                                ELSE 'False'
                                                END) as EditRights ,
                                            ( CASE 
                                                    WHEN MOP.ViewRights=1 THEN 'True'
                                                    ELSE 'False'
                                                    END ) as ViewRights ,
                                            ( CASE 
                                                    WHEN MOP.DeleteRights=1 THEN 'True'
                                                    ELSE 'False'
                                                    END ) as  DeleteRights  
                                            FROM menuOptionAccess AS MOP
                                            WHERE MOP.userId=?
                                            FOR JSON PATH) AS  varchar(max))""", (userId))
    row = await db.fetchone()
    if row[0] != None:
        for i in json.loads(row[0]):
            optionDic={}
            optionDic.update(i)
            dicData.append(optionDic['optionId'])
            await modifiedDataOptionsName(optionDic['optionId'],optionDic)
            data.append(optionDic)
        dic['OptionDetails']=data
    else:
        dic['OptionDetails']=data

async def modifiedDataOptionsEmployeeDetails(parkingUserId, db):
    await db.execute(f"""SELECT CAST((SELECT MOP.optionId,MOP.MenuOptionAccessId,(MOP.activeStatus) AS MenuOptionAccessActiveStatus,
											( CASE 
												WHEN MOP.AddRights=1 THEN 'True'
											ELSE 'False'
											END) AS AddRights ,
                                            ( CASE 
                                                WHEN MOP.EditRights=1 THEN 'True'
                                                ELSE 'False'
                                                END) as EditRights ,
                                            ( CASE 
                                                    WHEN MOP.ViewRights=1 THEN 'True'
                                                    ELSE 'False'
                                                    END ) as ViewRights ,
                                            ( CASE 
                                                    WHEN MOP.DeleteRights=1 THEN 'True'
                                                    ELSE 'False'
                                                    END ) as  DeleteRights  
                                            FROM menuOptionAccess AS MOP
                                            WHERE MOP.userId=?
                                            FOR JSON PATH) AS  varchar(max))""", (parkingUserId))
    row = await db.fetchone()
    if row[0] != None:
        return {"statusCode":1,"response":json.loads(row[0])}
    return []
        
async def getDetailsBasedOnUserId(userId,db):
    try:
        
        dic={}
        dicData=[]
        await asyncio.gather(modifiedDataUserName(userId,dic),
                            modifiedDataOptionsDetails(userId,dic,dicData,db)
                            
                            )
        if dic:
            if dic['userRole']=='E':
                response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/parkingOwnerMaster?parkingOwnerId={dic['parkingOwnerId']}")
                response = json.loads(response.text)
                if response['statusCode'] == 1:
                    res=await modifiedDataOptionsEmployeeDetails(response['response'][0]['userId'],db)
                    if res:
                        resData=[]
                        for i in res['response']:
                            if i['optionId'] not in dicData:
                                i['AddRights']='False'
                                i['EditRights']='False'
                                i['ViewRights']='False'
                                i['DeleteRights']='False'
                                await modifiedDataOptionsName(i['optionId'],i)
                                resData.append(i)
                        dic['OptionDetails']=dic['OptionDetails']+(resData)
                        return {"statusCode":1,"response": [dic]}
                    return {"statusCode":0,"response": "Error in getDetailsBasedOnUserId"}

            return {
                "statusCode":1,
                "response": [dic]
                
            }
        else:
            return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
       
    except Exception as e:
        print("Exception as getDetailsBasedOnUserId ",str(e))
        return {
            "statusCode": 0,
            "response": str(e)
            
        }

async def getDetailsBasedOnBranchId(branchId,db):
    try:
        data=[]
        dicData=[]
        getBranchIdDetails=await getUserId(branchId)
        
        for user in getBranchIdDetails:
            dic={}
            await asyncio.gather(modifiedDataUserName(user['userId'],dic),
                                modifiedDataOptionsDetails(user['userId'],dic,dicData,db)
                                
                                )
            if dic:
                if dic['userRole']=='E':
                    response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/parkingOwnerMaster?parkingOwnerId={dic['parkingOwnerId']}")
                    response = json.loads(response.text)
                    if response['statusCode'] == 1:
                        res=await modifiedDataOptionsEmployeeDetails(response['response'][0]['userId'],db)
                        if res:
                            resData=[]
                            for i in res['response']:
                                if i['optionId'] not in dicData:
                                    i['AddRights']='False'
                                    i['EditRights']='False'
                                    i['ViewRights']='False'
                                    i['DeleteRights']='False'
                                    await modifiedDataOptionsName(i['optionId'],i)
                                    resData.append(i)
                            dic['OptionDetails']=dic['OptionDetails']+(resData)
                            
                            data.append(dic)
                else:
                    data.append(dic) 
        if len(data)!=0:
           return {
            "statusCode": 1,
            "response": data
            
        }    
        
        else:
            return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
        
    except Exception as e:
        print("Exception as getDetailsBasedOnBranchId ",str(e))
        return {
            "statusCode": 0,
            "response": str(e)
            
        }
async def getMenuOptionsAccessDetails(db):
    try:
        data=[]
        dicData=[]
        await db.execute(f"""SELECT CAST((SELECT DISTINCT userId
                                                FROM menuOptionAccess
                                                  FOR JSON PATH) AS  varchar(max))""")
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic={}
                await asyncio.gather(modifiedDataUserName(i['userId'],dic),
                                    modifiedDataOptionsDetails(i['userId'],dic,dicData,db)
                                    
                                    )
                if dic:
                    if dic['userRole']=='E':
                        response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/parkingOwnerMaster?parkingOwnerId={dic['parkingOwnerId']}")
                        response = json.loads(response.text)
                        if response['statusCode'] == 1:
                            res=await modifiedDataOptionsEmployeeDetails(response['response'][0]['userId'],db)
                            if res:
                                resData=[]
                                for i in res['response']:
                                    if i['optionId'] not in dicData:
                                        i['AddRights']='False'
                                        i['EditRights']='False'
                                        i['ViewRights']='False'
                                        i['DeleteRights']='False'
                                        await modifiedDataOptionsName(i['optionId'],i)
                                        resData.append(i)
                                dic['OptionDetails']=dic['OptionDetails']+(resData)
                                
                                data.append(dic)
                    else:
                        data.append(dic) 
            if len(data)!=0:
                return {
                    "statusCode": 1,
                    "response": data
                    
                }    
            
            else:
                return {
                "statusCode": 0,
                "response": "Data Not Found"
                
            }
        
    except Exception as e:
        print("Exception as getMenuOptionsAccessDetails ",str(e))
        return {
            "statusCode": 0,
            "response": str(e)
            
        }
@menuOptionAccessRouter.get('')
async def getMenuOptionsAccess(userId:Optional[int]=Query(None),branchId:Optional[str]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        if userId:
            return await getDetailsBasedOnUserId(userId, db)
        elif branchId:
            return await getDetailsBasedOnBranchId(branchId, db)
        else:
            return await getMenuOptionsAccessDetails(db)
    except Exception as e:
        print("Exception as getMenuOptionsAccess ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@menuOptionAccessRouter.post('')
async def postMenuOptionAccess(request:schemas.MenuOptionAccess,db:Cursor = Depends(get_cursor)):
    try:
        r = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.optionDetails)
        await db.execute(f"""DECLARE @varRes NVARCHAR(400);
                            DECLARE @varStatus NVARCHAR(1);
                            EXEC [dbo].[postMenuOptionAccess]
                            @parkingOwnerId=?,
                            @userId =?,
                            @moduleId =?,
                            @createdBy =?,
                            @optionDetailsJson =?,
                            @outputVal = @varRes OUTPUT,
                            @outputStatus = @varStatus OUTPUT
                            SELECT @varRes AS varRes,@varStatus AS varStatus""",
                            (
                                request.parkingOwnerId,
                                request.userId,
                                request.moduleId,
                                request.createdBy,
                                json.dumps(r)
                            ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postMenuOptionAccess ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@menuOptionAccessRouter.put('')
async def putMenuOptionAccess(request:schemas.ListPutMenuOptionAccess,db:Cursor = Depends(get_cursor)):
    try:
        r = Parallel(n_jobs=-1, verbose=True)(delayed(callFunction)(i) for i in request.menuOptionAccessDetails)
        await db.execute(f"EXEC [dbo].[putMenuOptionAccess] @menuOptionJsonData=?", (json.dumps(r,indent=4, sort_keys=True, default=str)))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putMenuOptionAccess ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@menuOptionAccessRouter.delete('')
async def deleteMenuOptionAccess(activeStatus:str,MenuOptionAccessId:int,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE menuOptionAccess SET activeStatus=? WHERE MenuOptionAccessId=?",activeStatus,MenuOptionAccessId)
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
        print("Exception as deleteMenuOptionAccess ",str(e))
        return{"statusCode":0,"response":"Server Error"}