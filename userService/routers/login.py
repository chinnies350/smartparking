from sqlite3 import Cursor
from fastapi.routing import APIRouter
from fastapi import Depends
from routers.config import get_cursor
from dotenv import load_dotenv
import re
import json
import os
import routers

load_dotenv()

loginRouter = APIRouter(prefix='/login')


async def getUserDetailsBasedOnEmployee(userId):
    try:
        url=f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/employeeMaster?userId={userId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:
                return response['response']
        return {}
    except Exception as e:
        print(f'error in getUserDetailsBasedOnBranchId {str(e)}')
        return {}

async def getUserDetailsBasedOnAdmin(userId):
    try:
        url=f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/parkingOwnerMaster?userId={userId}"
        response = await routers.client.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            for i in response['response']:
                return response['response']
        return {}
    except Exception as e:
        print(f'error in getUserDetailsBasedOnAdmin {str(e)}')
        return {}

async def modifiedDataUserDetails(userId,dic):
    res  = await getUserDetailsBasedOnEmployee(userId)
    if res:
        dic['empDesignationName']=res['empDesignationName']
        dic['branchId']=res['branchId']
        dic['parkingOwnerId']=res['parkingOwnerId']
        dic['floorId']=res['floorId']
    else:
        res=await getUserDetailsBasedOnAdmin(userId)
        if res:
            dic['empDesignationName']=None
            dic['branchId']=None
            dic['parkingOwnerId']=res['parkingOwnerId']
            dic['floorId']=None
        else:
            dic['empDesignationName']=None
            dic['branchId']=None
            dic['parkingOwnerId']=None
            dic['floorId']=None
        


@loginRouter.get('')
async def getLogin(user:str,password:str,db:Cursor = Depends(get_cursor)):
    try:
        regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')
        if len(user)==10:
            data =[]
            await db.execute(f"""SELECT userId FROM userMaster WHERE phoneNumber=?""",(user))
            row = await db.fetchone()
            if row[0] == None:
                return {
                        'statusCode':0,
                        'response':'check your userName'
                    }
            await db.execute(f"""SELECT CAST((SELECT um.userId,um.userName,um.emailId,um.userRole
                                        FROM userMaster AS um
                                        WHERE um.phoneNumber=? AND um.password COLLATE Latin1_General_CS_AS=? and um.activeStatus='A' FOR JSON PATH) AS VARCHAR(MAX))""",(user,password))
            
            row=await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await modifiedDataUserDetails(dic['userId'],dic)
                    data.append(dic)
        elif re.fullmatch(regex, user):
            data =[]
            await db.execute(f"""SELECT userId FROM userMaster WHERE emailId=?""", (user))
            row = await db.fetchone()
            
            if row[0] == None:
                return {
                        'statusCode':0,
                        'response':'check your userName'
                    }
            await db.execute(f"""SELECT CAST((SELECT um.userId,um.userName,um.emailId,um.userRole
                                        FROM userMaster AS um
                                        WHERE um.emailId=? AND um.password COLLATE Latin1_General_CS_AS=? and um.activeStatus='A' FOR JSON PATH) AS VARCHAR(MAX))""",(user,password))
            
            row=await db.fetchone()
            
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await modifiedDataUserDetails(dic['userId'],dic)
                    data.append(dic)
        else:
            data =[]
            await db.execute(f"""SELECT userId FROM userMaster WHERE userName  COLLATE Latin1_General_CS_AS=?""", (user))
            row = await db.fetchone()
            if row[0] == None:
                return {
                        'statusCode':0,
                        'response':'check your userName'
                    }
            await db.execute(f"""SELECT CAST((SELECT um.userId,um.userName,um.emailId,um.userRole
                                        FROM userMaster AS um
                                        WHERE um.userName  COLLATE Latin1_General_CS_AS=? AND um.password COLLATE Latin1_General_CS_AS=? and um.activeStatus='A' FOR JSON PATH) AS VARCHAR(MAX))""",(user,password))

            
            row=await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await modifiedDataUserDetails(dic['userId'],dic)
                    data.append(dic)
        
        if len(data)!=0:
            return {"statusCode": 1,"response":data}
        else:
            return {
                    'statusCode':0,
                    'response': 'Wrong password. Try again or click ‘Forgot password’ to reset it.'
                }  
            

    except Exception as e:
        print("Exception as getLogin ",str(e))
        return {"statusCode":0,"response":"Server Error"}