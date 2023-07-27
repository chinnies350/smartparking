from  sqlalchemy import create_engine
import json,os
import requests
from routers.eventsServer import publish
from dotenv import load_dotenv
load_dotenv()
from task import postBlockName

engine = create_engine("mssql+pyodbc://sqldeveloper:SqlDeveloper$@192.168.1.221/parking_owner_service?driver=ODBC+Driver+17+for+SQL+Server")

async def postEmployeeMaster(request):
    # try:
    with engine.connect() as cur:
        result = cur.execute(f"""INSERT INTO employeeMaster(parkingOwnerId ,branchId ,blockId ,floorId ,userId ,DOJ ,empType ,empDesignation ,shiftId ,createdBy ,createdDate)
                            VALUES(?,?,?,?,?,?,?,?,?,?,GETDATE())""", (
                                request.get("parkingOwnerId") if request.get("parkingOwnerId") else None ,
                                request.get("branchId") if request.get("branchId") else None ,
                                request.get("blockId") if request.get("blockId") else None ,
                                request.get("floorId") if request.get("floorId") else None ,
                                request.get("userId") if request.get("userId") else None ,
                                request.get("DOJ") if request.get("DOJ") else None ,
                                request.get("empType") if request.get("empType") else None ,
                                request.get("empDesignation") if request.get("empDesignation") else None ,
                                request.get("shiftId") if request.get("shiftId") else None ,
                                request.get("createdBy") if request.get("createdBy") else None
                                
                            ))
        result.close()
    pass

async def putEmployeeMaster(request):
    with engine.connect() as cur:
        result = cur.execute(f"""
                                UPDATE employeeMaster SET parkingOwnerId=?, branchId=?, blockId=?, floorId=?, userId=?, DOJ=? ,empType=?, empDesignation=?, shiftId=? WHERE employeeId=?
                                """, (
                                    request.parkingOwnerId,
                                    request.branchId,
                                    request.blockId,
                                    request.floorId,
                                    request.DOJ,
                                    request.empType,
                                    request.empDesignation,
                                    request.shiftId,
                                    request.employeeId
                                ))
        result.close()
    
    pass

async def getUserDetailsBasedOnUserId(userId):
    try:
        url=f"{os.getenv('USER_SERVICE_URL')}/userMaster?userId={userId}"
        response = requests.get(url)
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return {}
    except Exception as e:
        print(f'error in getUserDetailsBasedOnBranchId {str(e)}')
        return {}

async def updateCancellationReason(message):
    
    with engine.connect() as cur:
        result=cur.execute(f"""EXEC [dbo].[cancellationReasonUpdate] ?,?""",(message['cancellationReason'],message['userId']))
        row=result.fetchone()
        result.close()
        if row[1]==1:
            if message['approvalStatus']=='C':
                await publish(queueName='notificationService', message = {
                            'action':'Owner Cancellation',
                            'body':{
                                'customerName':message['customerName'],
                                'cancellationReason':message['cancellationReason'],
                                'parkingName':row[2],
                                'emailId':message['emailId'],
                                'phoneNo':message['phoneNo']
                            }
                        })
            else:
                await publish(queueName='notificationService', message = {
                            'action':'Owner',
                            'body':{
                                'customerName':message['customerName'],
                                'parkingName':row[2],
                                'emailId':message['emailId'],
                                'phoneNo':message['phoneNo']
                            }
                        }) 
async def branchApproval(message):
    
    with engine.connect() as cur:
        result=cur.execute(f"""EXEC [dbo].[branchCancellationReasonUpdate] ?,?,?""",(message['cancellationReason'],message['branchId'],message['approvalStatus']))
        row=result.fetchone()
        result.close()
        
        if row[1]==1:
            userDetails=await getUserDetailsBasedOnUserId(row[5])
            if message['approvalStatus']=='C':
                await publish(queueName='notificationService', message = {
                            'action':'Branch Cancellation',
                            'body':{
                                'customerName':userDetails[0]['userName'],
                                'cancellationReason':message['cancellationReason'],
                                'parkingName':row[2],
                                'branchName':row[3],
                                'emailId':userDetails[0]['emailId'],
                                'phoneNo':userDetails[0]['phoneNumber']
                            }
                        })
            else:
                await publish(queueName='notificationService', message = {
                            'action':'Branch',
                            'body':{
                                'customerName':userDetails[0]['userName'],
                                'parkingName':row[2],
                                'branchName':row[3],
                                'emailId':userDetails[0]['emailId'],
                                'phoneNo':userDetails[0]['phoneNumber']
                            }
                        })
async def blockApproval(message):
    
    with engine.connect() as cur:
        result=cur.execute(f"""EXEC [dbo].[blockCancellationReasonUpdate] ?,?,?""",(message['cancellationReason'],message['branchId'],message['approvalStatus']))
        row=result.fetchone()
        result.close()
        if row[1]==1:
            userDetails=await getUserDetailsBasedOnUserId(row[5])
            if message['approvalStatus']=='C':
                await publish(queueName='notificationService', message = {
                            'action':'Block Cancellation',
                            'body':{
                                'customerName':userDetails[0]['userName'],
                                'cancellationReason':message['cancellationReason'],
                                'branchName':row[2],
                                'blockName':row[3],
                                'emailId':userDetails[0]['emailId'],
                                'phoneNo':userDetails[0]['phoneNumber']
                            }
                        })
            else:
                await publish(queueName='notificationService', message = {
                            'action':'Block',
                            'body':{
                                'customerName':userDetails[0]['userName'],
                                'branchName':row[2],
                                'blockName':row[3],
                                'emailId':userDetails[0]['emailId'],
                                'phoneNo':userDetails[0]['phoneNumber']
                            }
                        })
        # row = result.fetchone()

async def postBlockMaster(request):
    # try:
    with engine.connect() as cur:
        result = cur.execute(f"""EXEC [dbo].[postBlockMaster]
                                        @parkingOwnerId=?,
                                        @branchId=?,
                                        @blockName=?,
                                        @activeStatus=?,
                                        @approvalStatus=?,
                                        @createdBy=?
                                        """, (
                                request.get("parkingOwnerId") if request.get("parkingOwnerId") else None ,
                                request.get("branchId") if request.get("branchId") else None ,
                                request.get("blockName") if request.get("blockName") else None ,
                                request.get("activeStatus") if request.get("activeStatus") else None ,
                                request.get("approvalStatus") if request.get("approvalStatus") else None ,
                                request.get("createdBy") if request.get("createdBy") else None   
                            ))
        rows=result.fetchone()
        result.close()
        if int(rows[1])==1:
            postBlockName.delay(int(rows[2]),request['blockName'])
            if request['floorOption']=='N':
                await publish(queueName="slotManagement", message={
                                                    'action':'postFloorMaster',
                                                    'body':{
                                                        "parkingOwnerId" :request.get("parkingOwnerId") if request.get("parkingOwnerId") else None ,
                                                        "branchId":  request.get("branchId") if request.get("branchId") else None ,
                                                        "blockId" :int(rows[2]),
                                                        "squareFeet":request.get("squareFeet") if request.get("squareFeet") else None ,
                                                        "floorName" :request.get("floorName") if request.get("floorName") else None ,
                                                        "floorType":request.get("floorType") if request.get("floorType") else None ,
                                                        "activeStatus":'A',
                                                        "createdBy":request.get("createdBy") if request.get("createdBy") else None 
                                                        
                                                    }
                                                    })
    pass



functionMap = {"postEmployeeMaster": postEmployeeMaster,
                "putEmployeeMaster": putEmployeeMaster,
                'updateCancellationReason':updateCancellationReason,
                'branchApproval':branchApproval,
                'blockApproval':blockApproval,
                "postBlockMaster": postBlockMaster}

async def callback(message):
    message = json.loads(message)
    await functionMap[message["action"]](message['body'])