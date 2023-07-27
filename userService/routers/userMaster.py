from fastapi.routing import APIRouter
from typing import Optional
from fastapi import Query
import routers
from routers import Response
from fastapi import Depends
from routers.config import get_cursor
from aioodbc.cursor import Cursor
import os
from dotenv import load_dotenv
import json
import schemas
import datetime
from routers.eventServer import publish
from task import postUserName,signUpData


load_dotenv()

router = APIRouter(prefix='/userMaster',tags=['userMaster'])
routerApproval = APIRouter(prefix='/approvalStatus',tags=['approvalStatus'])
routerToken = APIRouter(prefix='/updateRegistrationToken', tags=['updateRegistrationToken'])
# async def getAdminDetailsBasedOnUserId(userId):
#     response = await routers.client.get(f"http://{os.getenv('PARKING_OWNER_SERVICE_URL')}:{os.getenv('PARKING_OWNER_SERVICE_PORT')}/parkingOwnerMaster")
#     return response.text

async def getEmployeeDetailsBasedOnUserId(userId):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/employeeMaster?userId={userId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return {}
    except Exception as e:
        print("Exception as getEmployeeDetailsBasedOnUserId ",str(e))
        return {}

async def getEmployeeDetialsBasedOnBlockId(blockId):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/employeeMaster?blockId={blockId}")
        return json.loads(response.text)
    except Exception as e:
        print("Exception as getEmployeeDetialsBasedOnBlockId ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def getEmployeeDetialsBasedOnFloorId(floorId):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/employeeMaster?floorId={floorId}")
        return json.loads(response.text)
    except Exception as e:
        print("Exception as getEmployeeDetialsBasedOnFloorId ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def getEmployeeDetialsBasedOnBranchId(branchId):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/employeeMaster?branchId={branchId}")
        return json.loads(response.text)
    except Exception as e:
        print("Exception as getEmployeeDetialsBasedOnBranchId ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def getEmployeeDetialsBasedOnBranchIdEmpCheck(branchId):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/employeeMaster?branchId={branchId}&empType=-1")
        return json.loads(response.text)
    except Exception as e:
        print("Exception as getEmployeeDetialsBasedOnBranchIdEmpCheck ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }


async def getEmployeeDetialsBasedOnParkingOwnerId(parkingOwnerId):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/employeeMaster?parkingOwnerId={parkingOwnerId}")
        return json.loads(response.text)
    except Exception as e:
        print("Exception as getEmployeeDetialsBasedOnParkingOwnerId ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def getUserDataBasedOnUserId(userId, db):
    try:
        await db.execute(f"""
                            SELECT CAST((SELECT * ,
                                ISNULL((SELECT am.addressId,am.address,am.alternatePhoneNumber,am.district,am.state,am.city,am.pincode FROM addressMaster AS am WHERE am.userId=userMaster.userId FOR JSON PATH),'[]')AS addressDetails
                            FROM userMaster
                            WHERE userId = ?
                            FOR JSON PATH) as VARCHAR(max))
                        """, (userId))
        
        row = await db.fetchone()
        if row[0] != None:
            return json.loads(row[0])[0]
        return {}
    
    except Exception as e:
        print("Exception as getUserDataBasedOnUserId ",str(e))
        return {}

async def getUserDataBasedOnUserIdAndUserRole(userId, userRole, db):
    try:
        await db.execute(f"""
                            SELECT CAST((SELECT * ,
                                ISNULL((SELECT am.addressId,am.address,am.alternatePhoneNumber,am.district,am.state,am.city,am.pincode FROM addressMaster AS am WHERE am.userId=userMaster.userId FOR JSON PATH),'[]')AS addressDetails
                            FROM userMaster
                            WHERE userId = ? AND userRole=?
                            FOR JSON PATH) as VARCHAR(max))
                        """, (userId, userRole))
        
        row = await db.fetchone()
        if row[0] != None:
            return json.loads(row[0])[0]
        return {}
    
    except Exception as e:
        print("Exception as getUserDataBasedOnUserIdAndUserRole ",str(e))
        return {}

async def getUserDataBasedOnUserIdAndUserRoleAndActiveStatus(userId, userRole, activeStatus, db):
    try:
        await db.execute(f"""
                            SELECT CAST((SELECT * ,
                                ISNULL((SELECT am.addressId,am.address,am.alternatePhoneNumber,am.district,am.state,am.city,am.pincode FROM addressMaster AS am WHERE am.userId=userMaster.userId FOR JSON PATH),'[]')AS addressDetails
                            FROM userMaster
                            WHERE userId = ? AND userRole=? AND activeStatus=?
                            FOR JSON PATH) as VARCHAR(max))
                        """, (userId, userRole,activeStatus))
        
        row = await db.fetchone()
        if row[0] != None:
            return json.loads(row[0])[0]
        return {}
    
    except Exception as e:
        print("Exception as getUserDataBasedOnUserIdAndUserRoleAndActiveStatus ",str(e))
        return {}

async def getEmployeeDetialsBasedOnParkingOwnerIdAndEmpDesignation(parkingOwnerId, empDesignation):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/employeeMaster?parkingOwnerId={parkingOwnerId}&empDesignation={empDesignation}")
        return json.loads(response.text)
    except Exception as e:
        print("Exception as getEmployeeDetialsBasedOnParkingOwnerIdAndEmpDesignation ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def getEmployeeDetialsBasedOnbranchIdAndEmpDesignation(branchId, empDesignation):
    try:
        response = await routers.client.get(f"{os.getenv('PARKING_OWNER_SERVICE_URL')}/employeeMaster?branchId={branchId}&empDesignation={empDesignation}")
        return json.loads(response.text)
    except Exception as e:
        print("Exception as getEmployeeDetialsBasedOnbranchIdAndEmpDesignation ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def mainContactBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT * 
                                FROM userMaster
                                WHERE mainContactName=?) AS VARCHAR(MAX))""",(mainContactName)) 
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    dic.update(await getEmployeeDetailsBasedOnUserId(dic['userId']))
                    data.append(dic)
            return {
                "response":data,
                "statusCode":1
            }
        return {
            "response":'Data Not Found',
            "statusCode":0
        }
    except Exception as e:
        print("Exception as mainContactBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }


async def userIdBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    data = []
    try:
        await db.execute(f"""SELECT CAST((SELECT * ,
                                            ISNULL((SELECT am.addressId,am.address,am.alternatePhoneNumber,am.district,am.state,am.city,am.pincode FROM addressMaster AS am WHERE am.userId=userMaster.userId FOR JSON PATH),'[]')AS addressDetails
                                        FROM userMaster
                                        
                                        WHERE userId=?

                                        FOR JSON PATH) AS VARCHAR(MAX))""", (userId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                dic.update(await getEmployeeDetailsBasedOnUserId(dic['userId']))
                data.append(dic)
            return {
                "response":data,
                "statusCode":1
            }

        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as userIdBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def phoneNumberBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    data = []
    try:
        await db.execute(f"""SELECT CAST((SELECT userMaster.* ,
                                            ISNULL((SELECT am.addressId,am.address,am.alternatePhoneNumber,am.district,am.state,am.city,am.pincode FROM addressMaster AS am WHERE am.userId=userMaster.userId FOR JSON PATH),'[]')AS addressDetails
                                        FROM userMaster
                                        
                                        WHERE phoneNumber=?

                                        FOR JSON PATH) AS VARCHAR(MAX))""", (phoneNumber))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                dic.update(await getEmployeeDetailsBasedOnUserId(dic['userId']))
                data.append(dic)
            return {
                "response":data,
                "statusCode":1
            }

        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as phoneNumberBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def emailIdBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    data = []
    try:
        await db.execute(f"""SELECT CAST((SELECT userMaster.* ,
                                            ISNULL((SELECT am.addressId,am.address,am.alternatePhoneNumber,am.district,am.state,am.city,am.pincode FROM addressMaster AS am WHERE am.userId=userMaster.userId FOR JSON PATH),'[]')AS addressDetails
                                        FROM userMaster
                                        
                                        WHERE emailId=?

                                        FOR JSON PATH) AS VARCHAR(MAX))""", (emailId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                dic.update(await getEmployeeDetailsBasedOnUserId(dic['userId']))
                data.append(dic)
            return {
                "response":data,
                "statusCode":1
            }

        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as emailIdBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def activeStatusBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    data = []
    try:
        await db.execute(f"""SELECT CAST((SELECT userMaster.* ,
                                            ISNULL((SELECT am.addressId,am.address,am.alternatePhoneNumber,am.district,am.state,am.city,am.pincode FROM addressMaster AS am WHERE am.userId=userMaster.userId FOR JSON PATH),'[]')AS addressDetails
                                        FROM userMaster
                                        
                                        WHERE activeStatus=?

                                        FOR JSON PATH) AS VARCHAR(MAX))""", (activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                dic.update(await getEmployeeDetailsBasedOnUserId(dic['userId']))
                data.append(dic)
            return {
                "response":data,
                "statusCode":1
            }

        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as activeStatusBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def blockIdBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    try:
        data = []
        response = await getEmployeeDetialsBasedOnBlockId(blockId)
        if response['statusCode'] == 1:
            for i in response['response']:
                i.update(await getUserDataBasedOnUserId(i['userId'], db))
                data.append(i)
            return {
                'response': data,
                "statusCode": 1
            }
        return {
            'response': 'Data Not Found',
            'statusCode':0
        }
    except Exception as e:
        print("Exception as blockIdBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def floorIdBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    try:
        data = []
        response = await getEmployeeDetialsBasedOnFloorId(floorId)
        if response['statusCode'] == 1:
            for i in response['response']:
                i.update(await getUserDataBasedOnUserId(i['userId'], db))
                data.append(i)
            return {
                'response': data,
                "statusCode": 1
            }
        return {
            'response': 'Data Not Found',
            'statusCode':0
        }
    except Exception as e:
        print("Exception as floorIdBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }


async def branchIdBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    try:
        data = []
        response = await getEmployeeDetialsBasedOnBranchId(branchId)
        if response['statusCode'] == 1:
            for i in response['response']:
                i.update(await getUserDataBasedOnUserId(i['userId'], db))
                data.append(i)
            return {
                'response': data,
                "statusCode": 1
            }
        return {
            'response': 'Data Not Found',
            'statusCode':0
        }
    except Exception as e:
        print("Exception as branchIdBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def parkingOwnerIdBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    try:
        data = []
        response = await getEmployeeDetialsBasedOnParkingOwnerId(parkingOwnerId)
        if response['statusCode'] == 1:
            for i in response['response']:
                i.update(await getUserDataBasedOnUserId(i['userId'], db))
                data.append(i)
            return {
                'response': data,
                "statusCode": 1
            }
        return {
            'response': 'Data Not Found',
            'statusCode':0
        }
    except Exception as e:
        print("Exception as parkingOwnerIdBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def parkingOwnerIdAndUserRoleBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    try:
        data = []
        response = await getEmployeeDetialsBasedOnParkingOwnerId(parkingOwnerId)
        if response['statusCode'] == 1:
            for i in response['response']:
                resp = await getUserDataBasedOnUserIdAndUserRole(i['userId'], userRole, db)
                if resp:
                    i.update(await getUserDataBasedOnUserIdAndUserRole(i['userId'], userRole, db))
                    data.append(i)
            return {
                'response': data,
                "statusCode": 1
            }
        return {
            'response': 'Data Not Found',
            'statusCode':0
        }
    except Exception as e:
        print("Exception as parkingOwnerIdAndUserRoleBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }


async def userRoleBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    data = []
    try:
        await db.execute(f"""SELECT CAST((SELECT userMaster.* ,
                                            ISNULL((SELECT am.addressId,am.address,am.alternatePhoneNumber,am.district,am.state,am.city,am.pincode FROM addressMaster AS am WHERE am.userId=userMaster.userId FOR JSON PATH),'[]')AS addressDetails
                                        FROM userMaster
                                        
                                        WHERE userRole=?

                                        FOR JSON PATH) AS VARCHAR(MAX))""", (userRole))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                dic.update(await getEmployeeDetailsBasedOnUserId(dic['userId']))
                data.append(dic)
            return {
                "response":data,
                "statusCode":1
            }

        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as userRoleBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }


async def userRoleAndApprovalStatusBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    data = []
    try:
        await db.execute(f"""SELECT CAST((SELECT userMaster.* ,
                                            ISNULL((SELECT am.addressId,am.address,am.alternatePhoneNumber,am.district,am.state,am.city,am.pincode FROM addressMaster AS am WHERE am.userId=userMaster.userId FOR JSON PATH),'[]')AS addressDetails
                                        FROM userMaster
                                        
                                        WHERE userRole=? AND approvalStatus=?

                                        FOR JSON PATH) AS VARCHAR(MAX))""", (userRole, approvalStatus))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                dic.update(await getEmployeeDetailsBasedOnUserId(dic['userId']))
                data.append(dic)
            return {
                "response":data,
                "statusCode":1
            }

        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as userRoleAndApprovalStatusBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }


async def approvalStatusBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    data = []
    try:
        await db.execute(f"""SELECT CAST((SELECT userMaster.* ,
                                            ISNULL((SELECT am.addressId,am.address,am.alternatePhoneNumber,am.district,am.state,am.city,am.pincode FROM addressMaster AS am WHERE am.userId=userMaster.userId FOR JSON PATH),'[]')AS addressDetails
                                        FROM userMaster
                                        WHERE approvalStatus=?
                                        FOR JSON PATH) AS VARCHAR(MAX))""", (approvalStatus))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                dic.update(await getEmployeeDetailsBasedOnUserId(dic['userId']))
                data.append(dic)
            return {
                "response":data,
                "statusCode":1
            }

        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as approvalStatusBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def parkingOwnerIdAndEmpDesignationBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    try:
        data = []
        response = await getEmployeeDetialsBasedOnParkingOwnerIdAndEmpDesignation(parkingOwnerId, empDesignation)
        if response['statusCode'] == 1:
            for i in response['response']:
                resp = await getUserDataBasedOnUserId(i['userId'], db)
                if resp:
                    i.update(await getUserDataBasedOnUserId(i['userId'], db))
                    data.append(i)
            return {
                'response': data,
                "statusCode": 1
            }
        return {
            'response': 'Data Not Found',
            'statusCode':0
        }
    except Exception as e:
        print("Exception as parkingOwnerIdAndEmpDesignationBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def branchIdAndEmpDesignationBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    try:
        data = []
        response = await getEmployeeDetialsBasedOnbranchIdAndEmpDesignation(branchId, empDesignation)
        if response['statusCode'] == 1:
            for i in response['response']:
                resp = await getUserDataBasedOnUserId(i['userId'], db)
                if resp:
                    i.update(await getUserDataBasedOnUserId(i['userId'], db))
                    data.append(i)
            return {
                'response': data,
                "statusCode": 1
            }
        return {
            'response': 'Data Not Found',
            'statusCode':0
        }
    except Exception as e:
        print("Exception as branchIdAndEmpDesignationBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def branchIdAndUserRoleBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    try:
        data = []
        response = await getEmployeeDetialsBasedOnBranchId(branchId)
        if response['statusCode'] == 1:
            for i in response['response']:
                resp = await getUserDataBasedOnUserIdAndUserRole(i['userId'], userRole, db)
                if resp:
                    i.update(resp)
                    data.append(i)
            return {
                'response': data,
                "statusCode": 1
            }
        return {
            'response': 'Data Not Found',
            'statusCode':0
        }
    except Exception as e:
        print("Exception as branchIdAndUserRoleBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }
async def branchIdUserRoleActiveStatusBasedDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    try:
        data = []
        response = await getEmployeeDetialsBasedOnBranchId(branchId)
        if response['statusCode'] == 1:
            for i in response['response']:
                resp = await getUserDataBasedOnUserIdAndUserRoleAndActiveStatus(i['userId'], userRole,activeStatus, db)
                
                if resp:
                    i.update(resp)
                    data.append(i)
            return {
                'response': data,
                "statusCode": 1
            }
        return {
            'response': 'Data Not Found',
            'statusCode':0
        }
    except Exception as e:
        print("Exception as branchIdUserRoleActiveStatusBasedDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def branchIdUserRoleActiveStatusBasedTypeDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    try:
        data = []
        response = await getEmployeeDetialsBasedOnBranchIdEmpCheck(branchId)
        print("response",response)
        if response['statusCode'] == 1:
            for i in response['response']:
                resp = await getUserDataBasedOnUserIdAndUserRoleAndActiveStatus(i['userId'], userRole,activeStatus, db)
                print("resp",resp)
                if resp:
                    i.update(resp)
                    data.append(i)
            return {
                'response': data,
                "statusCode": 1
            }
        return {
            'response': 'Data Not Found',
            'statusCode':0
        }
    except Exception as e:
        print("Exception as branchIdUserRoleActiveStatusBasedTypeDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

async def allDetails(parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db):
    data = []
    try:
        await db.execute(f"""SELECT CAST((SELECT * ,
                                            ISNULL((SELECT am.addressId,am.address,am.alternatePhoneNumber,am.district,am.state,am.city,am.pincode FROM addressMaster AS am WHERE am.userId=userMaster.userId FOR JSON PATH),'[]')AS addressDetails
                                        FROM userMaster
                                        FOR JSON PATH) AS VARCHAR(MAX))""")
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                dic.update(await getEmployeeDetailsBasedOnUserId(dic['userId']))
                data.append(dic)
            return {
                "response":dic,
                "statusCode":1
            }

        return {
            "response":"Data Not Found",
            "statusCode":0
        }
    except Exception as e:
        print("Exception as allDetails ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }


userDic = {
    "parkingOwnerId=False, userRole=False, empDesignation=False, approvalStatus=False, branchId=False, mainContactName=True, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": mainContactBasedDetails,
    "parkingOwnerId=False, userRole=False, empDesignation=False, approvalStatus=False, branchId=False, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=True, phoneNumber=False, emailId=False, type=False": userIdBasedDetails,
    "parkingOwnerId=False, userRole=False, empDesignation=False, approvalStatus=False, branchId=False, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=True, emailId=False, type=False": phoneNumberBasedDetails,
    "parkingOwnerId=False, userRole=False, empDesignation=False, approvalStatus=False, branchId=False, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=True, type=False": emailIdBasedDetails,
    "parkingOwnerId=False, userRole=False, empDesignation=False, approvalStatus=False, branchId=False, mainContactName=False, activeStatus=True, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": activeStatusBasedDetails,
    "parkingOwnerId=False, userRole=False, empDesignation=False, approvalStatus=False, branchId=False, mainContactName=False, activeStatus=False, blockId=True, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": blockIdBasedDetails,
    "parkingOwnerId=False, userRole=False, empDesignation=False, approvalStatus=False, branchId=False, mainContactName=False, activeStatus=False, blockId=False, floorId=True, userId=False, phoneNumber=False, emailId=False, type=False": floorIdBasedDetails,
    "parkingOwnerId=False, userRole=False, empDesignation=False, approvalStatus=False, branchId=True, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": branchIdBasedDetails,
    "parkingOwnerId=True, userRole=False, empDesignation=False, approvalStatus=False, branchId=False, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": parkingOwnerIdBasedDetails,
    "parkingOwnerId=True, userRole=True, empDesignation=False, approvalStatus=False, branchId=False, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": parkingOwnerIdAndUserRoleBasedDetails,
    "parkingOwnerId=False, userRole=True, empDesignation=False, approvalStatus=False, branchId=False, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": userRoleBasedDetails,
    "parkingOwnerId=False, userRole=True, empDesignation=False, approvalStatus=True, branchId=False, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": userRoleAndApprovalStatusBasedDetails,
    "parkingOwnerId=False, userRole=False, empDesignation=False, approvalStatus=True, branchId=False, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": approvalStatusBasedDetails,
    "parkingOwnerId=True, userRole=False, empDesignation=True, approvalStatus=False, branchId=False, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": parkingOwnerIdAndEmpDesignationBasedDetails,
    "parkingOwnerId=False, userRole=False, empDesignation=True, approvalStatus=False, branchId=True, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": branchIdAndEmpDesignationBasedDetails,
    "parkingOwnerId=False, userRole=True, empDesignation=False, approvalStatus=False, branchId=True, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": branchIdAndUserRoleBasedDetails,
    "parkingOwnerId=False, userRole=True, empDesignation=False, approvalStatus=False, branchId=True, mainContactName=False, activeStatus=True, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": branchIdUserRoleActiveStatusBasedDetails,
    "parkingOwnerId=False, userRole=True, empDesignation=False, approvalStatus=False, branchId=True, mainContactName=False, activeStatus=True, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=True": branchIdUserRoleActiveStatusBasedTypeDetails,
    "parkingOwnerId=False, userRole=False, empDesignation=False, approvalStatus=False, branchId=False, mainContactName=False, activeStatus=False, blockId=False, floorId=False, userId=False, phoneNumber=False, emailId=False, type=False": allDetails,
    
}


@router.get("")
async def userGet(parkingOwnerId:Optional[int]=Query(None),userRole:Optional[str]=Query(None),empDesignation:Optional[int]=Query(None),approvalStatus:Optional[str]=Query(None),branchId:Optional[int]=Query(None),mainContactName:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),blockId:Optional[int]=Query(None),floorId:Optional[int]=Query(None),userId:Optional[int]=Query(None),phoneNumber:Optional[str]=Query(None),emailId:Optional[str]=Query(None),type:Optional[str]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        st = f"parkingOwnerId={True if parkingOwnerId else False}, userRole={True if userRole else False}, empDesignation={True if empDesignation else False}, approvalStatus={True if approvalStatus else False}, branchId={True if branchId else False}, mainContactName={True if mainContactName else False}, activeStatus={True if activeStatus else False}, blockId={True if blockId else False}, floorId={True if floorId else False}, userId={True if userId else False}, phoneNumber={True if phoneNumber else False}, emailId={True if emailId else False}, type={True if type else False}"    
        return await userDic[st](parkingOwnerId, userRole, empDesignation, approvalStatus, branchId,mainContactName, activeStatus, blockId, floorId, userId, phoneNumber, emailId, type, db)
    except Exception as e:
        print("Exception as userGet ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }


@router.post('')
async def postUserData(request : schemas.UserMaster, db:Cursor = Depends(get_cursor)):
    try:
        query = "SELECT * FROM userMaster WHERE "
        li = []
        if request.phoneNumber:
            li.append(" phoneNumber = '{phoneNumber}' ")
        if request.emailId:
            li.append(" emailId = '{emailId}' ")
        if request.userName:
            li.append(" userName = '{userName}' ")

        query = query + 'or'.join(li)
        print(query)
        print(query.format(phoneNumber = request.phoneNumber, emailId = request.emailId, userName = request.userName))
        await db.execute(query.format(phoneNumber = request.phoneNumber, emailId = request.emailId, userName = request.userName))
        row = await db.fetchone()
        print("row",row)
        if row == None:
            await db.execute(f"""
                                EXEC [dbo].[postUsermaster] 
                                @userName =?,
								@password =?,
								@emailId =?,
								@phoneNumber =?,
								@mainContactName =?,
								@approvalStatus =?,
								@activeStatus =?,
								@walletAmt =?,
								@loyaltyPoints =?,
								@createdBy =?,
                                @imageUrl =?,
								@userRole =?,
								@alternatePhoneNumber =?,
								@address =?,
								@district =?, 
								@state =?,
								@city =?,
								@pincode =?,
                                @registrationToken=?
                                """,
                        (   request.userName,
                            request.password,
                            request.emailId,
                            request.phoneNumber,
                            request.mainContactName,
                            request.approvalStatus,
                            request.activeStatus,
                            request.walletAmt,
                            request.loyaltyPoints,
                            request.createdBy,
                            request.imageUrl,
                            request.userRole,
                            request.alternatePhoneNumber,
                            request.address,
                            request.district,
                            request.state,
                            request.city,
                            request.pincode,
                            request.registrationToken
                            ))
            # if db.rowcount:
            row = await db.fetchone()
            if row[1] == 1:
                postUserName.delay(row[2],request.userName,request.emailId)
                if request.DOJ!=None and request.empType!=None:
                    await publish(queueName="parkingOwnerService", message={
                                                'action':'postEmployeeMaster',
                                                'body':{
                                                    "parkingOwnerId" :request.parkingOwnerId,
                                                    "branchId": request.branchId ,
                                                    "blockId" :request.blockId,
                                                    "floorId":request.floorId ,
                                                    "userId" :row[2],
                                                    "DOJ":request.DOJ ,
                                                    "empType":request.empType ,
                                                    "empDesignation":request.empDesignation ,
                                                    "shiftId":request.shiftId ,
                                                    "createdBy":request.createdBy
                                                    
                                                }
                                                })
                if request.userRole=='C':
                    signUpData.delay({'emailId': request.emailId,'phoneNumber':request.phoneNumber})
                # await publish(queueName='notificationService', message = {
                #     'action':'signUp',
                #     'body':{
                #         'emailId': request.emailId,
                #         'phoneNo': request.phoneNumber
                #     }
                # })
                return {
                    'response':'Data Added Successfully',
                    'statusCode':1,
                    'userId':row[2]
                }
            return {
                'response': row[0],
                'statusCode':0
            }
                
        return {
            'response':'Data Already Exists',
            'statusCode':0
        }
    except Exception as e:
        print("Exception as postUserData ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }

@router.put('')
async def putUserMaster(request: schemas.PutUserMaster, db: Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""
                                EXEC [dbo].[putUsermaster] 
                                @userName =?,
								@password =?,
								@emailId =?,
								@phoneNumber =?,
								@walletAmt =?,
								@loyaltyPoints =?,
								@updatedBy =?,
								@userId =?,
                                @imageUrl =?,
								@alternatePhoneNumber =?,
								@address =?,
								@district =?, 
								@state =?,
								@city =?,
								@pincode =?,
                                @addressId=?
                                """,
                        (
                            request.userName,
                            request.password,
                            request.emailId,
                            request.phoneNumber,
                            request.walletAmt,
                            request.loyaltyPoints,
                            request.updatedBy,
                            request.userId,
                            request.imageUrl,
                            request.alternatePhoneNumber,
                            request.address,
                            request.district,
                            request.state,
                            request.city,
                            request.pincode,
                            request.addressId
                            ))
        row = await db.fetchone()
        if row[1] == 1:
            postUserName.delay(request.userId,request.userName,request.emailId)
            if request.empDesignation != None and request.shiftId != None and request.DOJ != None and request.empType != None and request.employeeId != None:
                await publish(queueName='parkingOwnerService', message={
                    'action':'putEmployeeMaster',
                    'body': {
                        "parkingOwnerId": request.parkingOwnerId,
                        "branchId": request.branchId,
                        "blockId": request.blockId,
                        "floorId": request.floorId,
                        "DOJ": request.DOJ,
                        "empType": request.empType,
                        "empDesignation": request.empDesignation,
                        "shiftId": request.shiftId,
                        "employeeId": request.employeeId
                    }
                })
            return {
                'response': row[0],
                'statusCode': 1
            }
        return {
            'response': 'Data Not Updated',
            'statusCode': 0
        }
    except Exception as e:
        print("Exception as putUserMaster ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }


@router.delete('')
async def deleteuserMaster(userId: int,activeStatus:str, db:Cursor = Depends(get_cursor)):
    try:
        await db.execute("UPDATE UserMaster SET activeStatus=? WHERE userId=?",activeStatus,userId) 
        await db.commit()
        # result.close()
        if db.rowcount >= 1:
            if activeStatus=='D':
                return Response("deactiveMsg")
            else:
                return Response("ActiveMsg")
        else:
            return Response("NotFound")

    except Exception as e:
        print("Exception as deleteuserMaster ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        } 

@routerApproval.put('')
async def putApprovalStatus(userId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),blockId:Optional[int]=Query(None),approvalStatus:Optional[str]=Query(None),cancellationReason:Optional[str]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        if userId:
            await db.execute(f"""EXEC [dbo].[adminApproval] ?,?""",(userId,approvalStatus))
            row=await db.fetchone()
            await db.commit()
            if row[1] == 1:
                approvalVal='Owner Approved Successfully'
                cancelVal='Owner Approval is Cancelled'
                await publish(queueName='parkingOwnerService', message = {
                        'action':'updateCancellationReason',
                        'body':{
                            'userId':userId,
                            'cancellationReason':cancellationReason,
                            'approvalStatus':approvalStatus,
                            'customerName':row[2],
                            'emailId':row[3],
                            'phoneNo':row[4]
                        }
                    })
            
        elif branchId:
                approvalVal='Branch Approved Successfully'
                cancelVal='Branch Approval is Cancelled'
                await publish(queueName='parkingOwnerService', message = {
                        'action':'branchApproval',
                        'body':{
                            'branchId':branchId,
                            'cancellationReason':cancellationReason,
                            'approvalStatus':approvalStatus
                            
                        }
                    })
        elif blockId:
                approvalVal='Block Approved Successfully'
                cancelVal='Branch Approval is Cancelled'
                await publish(queueName='parkingOwnerService', message = {
                        'action':'blockApproval',
                        'body':{
                            'branchId':blockId,
                            'cancellationReason':cancellationReason,
                            'approvalStatus':approvalStatus
                            
                        }
                    })
        else:
            return{"statusCode": 0,"response": 'Please Enter Valid Data'}
        if approvalStatus!='C':
            return{"statusCode": 1,"response": approvalVal}
        else:
            return{"statusCode": 1,"response": cancelVal}


    except Exception as e:
        print("Exception as putApprovalStatus ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        } 



@routerToken.put('')
async def updateRegistrationTokenFun(request: schemas.UpdateRegistrationToken, db:Cursor = Depends(get_cursor)):
    try:
        await db.execute("UPDATE userMaster SET registrationToken=? WHERE userId=?", (request.registrationToken, request.userId)) 
        await db.commit()
        # result.close()
        if db.rowcount >= 1:
            return {
                    "response":"Data Updated Successfully",
                    "statusCode":1
                }
        else:
                return {
                    "response":"Data Not Updated",
                    "statusCode":0
                }

    except Exception as e:
        print("Exception as updateRegistrationTokenFun ",str(e))
        return {
            'response':"Server Error",
            "statusCode":0
        }