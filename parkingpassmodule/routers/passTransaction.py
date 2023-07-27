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
from joblib import Parallel, delayed
from dotenv import load_dotenv
from routers.eventServer import publish
from task import passTransaction
load_dotenv()

passTransactionRouter = APIRouter(prefix='/passTransaction',tags=['passTransaction'])



async def getPassTransactionTaxId(taxId):
    try:
        response = await routers.client.get(f"{os.getenv('ADMIN_SERVICE_URL')}/taxMaster?taxId={taxId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            
            return response['response'][0]
        return ""
    except Exception as e:
        print("Exception as getPassTransactionTaxId ",str(e))
        return ""

async def getPassTransactionIdTypeVehicleHeader(parkingPassTransId,type):
    
    try:
        response = await routers.client.get(f"{os.getenv('BOOKING_URL')}/vehicleHeader?parkingPassTransId={parkingPassTransId}&type={type}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return []
    except Exception as e:
        print("Exception as getPassTransactionIdTypeVehicleHeader ",str(e))
        return []

async def getPassTransactionUserId(userId):
    try:
        response = await routers.client.get(f"{os.getenv('USER_SERVICE_URL')}/userMaster?userId={userId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return {}
    except Exception as e:
        print("Exception as getPassTransactionUserId ",str(e))
        return {}

async def modifiedDataVehicleHeaderTypeDetails(parkingPassTransId,type):
    return await getPassTransactionIdTypeVehicleHeader(parkingPassTransId,type)

async def modifiedDataUserDetails(userId, dic):
    userDetails = await getPassTransactionUserId(userId)
    
    dic['userName']=userDetails[0]['userName']
    dic['userPhoneNumber']=userDetails[0]['phoneNumber']
    dic['imageUrl']=userDetails[0]['imageUrl']
    dic['emailId']=userDetails[0]['emailId']

async def modifiedDataUserDetail(userId, dic):
    userDetails = await getPassTransactionUserId(userId)
    dic['userName']=userDetails[0]['userName']
   


async def passTransactionIdDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pt.*,(CASE WHEN(GETDATE() BETWEEN  (CONVERT(DATETIME, CONVERT(CHAR(8), pt.validStartDate, 112) + ' ' + CONVERT(CHAR(8), pt.validStartTime, 108))) AND (CONVERT(DATETIME, CONVERT(CHAR(8), pt.validEndDate, 112) + ' ' + CONVERT(CHAR(8), pt.validEndTime, 108))))
												                THEN 'N'
											                ELSE
												                'Y'
												        END) as 'expiry',
                                                (SELECT pc.passType,pc.passCategory from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType
                                                FROM passTransaction as pt
                                                WHERE pt.parkingPassTransId = ?  FOR JSON PATH) AS  varchar(max))""", (parkingPassTransId))
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
        print("Exception as passTransactionIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
async def passTransactionIdTypeDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        data = []
        if type=='U':
            await db.execute(f"""SELECT CAST((SELECT pt.*,
                                                    (SELECT pc.passType,pc.passCategory from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType
                                                    FROM passTransaction as pt
                                                    WHERE pt.parkingPassTransId = ?  FOR JSON PATH) AS  varchar(max))""", (parkingPassTransId))
            row = await db.fetchone()
            if row[0] != None:
                for i in json.loads(row[0]):
                    dic = {}
                    dic.update(i)
                    await modifiedDataUserDetails(dic['userId'],dic)                 
                    data.append(dic)
                
                return {
                    "statusCode":1,
                    "response": data
                    
                }
            return {
                "statusCode": 0,
                "response": "Data Not Found"
                
            }
        elif type=='O':
            data=await modifiedDataVehicleHeaderTypeDetails(parkingPassTransId,'O')
            if len(data)!=0:
                return {
                    "statusCode":1,
                    "response": data
                    
                }
            else:
                return {
                "statusCode": 0,
                "response": "Data Not Found"
                
            }
        elif type=='I':
            data=await modifiedDataVehicleHeaderTypeDetails(parkingPassTransId,'I')
            if len(data)!=0:
                return {
                    "statusCode":1,
                    "response": data
                    
                }
            else:
                return {
                "statusCode": 0,
                "response": "Data Not Found"
                
            }

    except Exception as e:
        print("Exception as passTransactionIdTypeDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def passTransactionPassIdDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT pt.*,
                                                (SELECT pc.passType,pc.passCategory from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType
                                                FROM passTransaction as pt
                                                WHERE pt.passId = ?  FOR JSON PATH) AS  varchar(max))""", (passId))
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
        print("Exception as passTransactionPassIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def passTransactionPhoneNumberDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        
        await db.execute(f"""SELECT CAST((SELECT pt.*,
                                                (SELECT pc.passType,pc.  from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType
                                                FROM passTransaction as pt
                                                WHERE pt.phoneNumber = ?  FOR JSON PATH) AS  varchar(max))""", (phoneNumber))
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
        print("Exception as passTransactionPhoneNumberDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def passTransactionOwnerIdDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pt.*,
                                                (SELECT pc.passType,pc.passCategory from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType
                                                FROM passTransaction as pt
                                                WHERE pt.parkingOwnerId = ?  FOR JSON PATH) AS  varchar(max))""", (parkingOwnerId))
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
        print("Exception as passTransactionOwnerIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def passTransactionBranchIdDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pt.*,
                                                (SELECT pc.passType,pc.passCategory from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType
                                                FROM passTransaction as pt
                                                WHERE pt.branchId = ?  FOR JSON PATH) AS  varchar(max))""", (branchId))
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
        print("Exception as passTransactionBranchIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            }
async def passTransactionTaxIdDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pt.*,
                                                (SELECT pc.passType,pc.passCategory from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType 
                                                FROM passTransaction as pt
                                                WHERE pt.taxId = ?  FOR JSON PATH) AS  varchar(max))""", (taxId))
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
        print("Exception as passTransactionTaxIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def passTransactionTaxIdTypeDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        # type-T means taxMaxDate calculation
        await db.execute(f"""SELECT CAST(MAX(pt.createdDate) as date)AS passTransaction
                                FROM passTransaction as pt
                                WHERE pt.taxId = ?
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
        print("Exception as passTransactionTaxIdTypeDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def passTransactionPassUserIdDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pt.*,
                                                (SELECT pc.passType,pc.passCategory from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType 
                                                FROM passTransaction as pt
                                                WHERE pt.passId = ? AND pt.userId=?  FOR JSON PATH) AS  varchar(max))""", (passId,userId))
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
        print("Exception as passTransactionPassUserIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
async def passTransactionUserIdTypeDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        data=[]
        if type=='R':
            await db.execute(f"""SELECT CAST((SELECT * FROM (SELECT pt.parkingPassTransId,pt.passId,pt.parkingOwnerId,pt.parkingName,pt.branchId,pt.branchName,pt.userId,pt.phoneNumber,pt.vehicleType,pt.vehicleTypeName,pt.vehicleImageUrl,pt.validStartDate,pt.validEndDate,RIGHT(CONVERT(VARCHAR,pt.validStartTime, 100),7) AS validStartTime,RIGHT(CONVERT(VARCHAR,pt.validEndTime, 100),7) AS validEndTime,pt.amount,pt.tax,pt.totalAmount,pt.taxId,pt.paymentStatus,pt.paymentType,pt.walletCash,pt.cancellationStatus,pt.refundStatus,pt.cancellationCharges,pt.refundAmt,
						pt.cancellationReason,pt.transactionId,pt.bankName,pt.bankReferenceNumber,pt.offerId,pt.offerAmount,pt.activeStatus,pt.createdBy,pt.createdDate,pt.updatedBy,pt.updatedDate,(SELECT pc.passType,pc.passCategory from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType,
					                                        DATEDIFF(day,CAST(GETDATE() AS date),pt.validEndDate)AS remainingCount,(CASE WHEN(GETDATE() BETWEEN  (CONVERT(DATETIME, CONVERT(CHAR(8), pt.validStartDate, 112) + ' ' + CONVERT(CHAR(8), pt.validStartTime, 108))) AND (CONVERT(DATETIME, CONVERT(CHAR(8), pt.validEndDate, 112) + ' ' + CONVERT(CHAR(8), pt.validEndTime, 108))))
												THEN 'N'
											ELSE
												'Y'
												END) as 'expiry' 
                                                            FROM passTransaction as pt
                                                            WHERE pt.userId=?) as subTab WHERE remainingCount>0  FOR JSON PATH) AS  varchar(max))""", (userId))
        elif type=='E':
            await db.execute(f"""SELECT CAST((SELECT pt.*,(SELECT pc.passType,pc.passCategory from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType
							                    FROM passTransaction as pt
							                    WHERE userId=? AND DATEDIFF(day,CAST(GETDATE() AS date),pt.validEndDate)=1  FOR JSON PATH) AS  varchar(max))""", (userId))

        elif type=='N':
            await db.execute(f"""SELECT CAST((SELECT * 
                                                FROM (SELECT pt.*,
                                                            DATEDIFF(day,CAST(GETDATE() AS date),pt.validEndDate)AS remainingCount
                                                    
                                                    FROM passTransaction AS pt
                                                    WHERE pt.userId=?
                                                    AND NOT (GETDATE() BETWEEN  (CONVERT(DATETIME, CONVERT(CHAR(8), pt.validStartDate, 112) + ' ' + CONVERT(CHAR(8), pt.validStartTime, 108))) AND (CONVERT(DATETIME, CONVERT(CHAR(8), pt.validEndDate, 112) + ' ' + CONVERT(CHAR(8), pt.validEndTime, 108))))
                                                    ) as subTab WHERE remainingCount>0 FOR JSON PATH) AS varchar(max))""", (userId))

        elif type=='Y':
            await db.execute(f"""SELECT CAST((SELECT * 
                                                FROM (SELECT pt.*,
                                                            DATEDIFF(day,CAST(GETDATE() AS date),pt.validEndDate)AS remainingCount
                                                    
                                                    FROM passTransaction AS pt
                                                    WHERE pt.userId=?
                                                    AND (GETDATE() BETWEEN  (CONVERT(DATETIME, CONVERT(CHAR(8), pt.validStartDate, 112) + ' ' + CONVERT(CHAR(8), pt.validStartTime, 108))) AND (CONVERT(DATETIME, CONVERT(CHAR(8), pt.validEndDate, 112) + ' ' + CONVERT(CHAR(8), pt.validEndTime, 108))))
                                                    ) as subTab WHERE remainingCount>0 FOR JSON PATH) AS varchar(max))""", (userId))
        row = await db.fetchone()
        
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                await modifiedDataUserDetail(dic['userId'],dic)                 
                data.append(dic)
                
            return {
                "statusCode":1,
                "response": data
                
            }
        return {
            "statusCode": 0,
            "response": "Data Not Found"
            
        }
    except Exception as e:
        print("Exception as passTransactionUserIdTypeDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }


async def passTransactionUserIdDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pt.parkingPassTransId
                                                FROM passTransaction as pt
                                                WHERE pt.userId=?  FOR JSON PATH) AS  varchar(max))""", (userId))
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
        print("Exception as passTransactionUserIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

async def passTransactionBranchIdPassIdDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        data = []
        await db.execute(f"""SELECT CAST((SELECT pt.*,
                                                (SELECT pc.passType,pc.passCategory from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType
                                                FROM passTransaction as pt
                                                WHERE pt.branchId = ? AND pt.passId=? FOR JSON PATH) AS  varchar(max))""", (branchId,passId))
        row = await db.fetchone()
        if row[0] != None:
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
        print("Exception as passTransactionBranchIdDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            }

async def passTransactionDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        await db.execute(f"""SELECT CAST((SELECT pt.*,
                                        (SELECT pc.passType,pc.passCategory from parkingPassConfig as pc WHERE pt.passId=pc.parkingPassConfigId FOR JSON PATH)AS passType
                                        FROM passTransaction as pt
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
        print("Exception as passTransactionDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
        
async def passTransactionPhoneNumberTypeDetails(parkingPassTransId, passId, parkingOwnerId, branchId, taxId, userId, type,phoneNumber, db):
    try:
        await db.execute(f"""SELECT CAST((select top 1 parkingPassTransId from passTransaction where phoneNumber='{phoneNumber}' ORDER BY parkingPassTransId DESC
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
        print("Exception as passTransactionPhoneNumberTypeDetails ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }
        

parkingPassDict = {
   "parkingPassTransId=True, passId=False, parkingOwnerId=False, branchId=False, taxId=False, userId=False, type=False, phoneNumber=False":passTransactionIdDetails,
   "parkingPassTransId=False, passId=False, parkingOwnerId=False, branchId=False, taxId=False, userId=False, type=False, phoneNumber=True":passTransactionPhoneNumberDetails,
   "parkingPassTransId=True, passId=False, parkingOwnerId=False, branchId=False, taxId=False, userId=False, type=True, phoneNumber=False":passTransactionIdTypeDetails,
   "parkingPassTransId=False, passId=True, parkingOwnerId=False, branchId=False, taxId=False, userId=False, type=False, phoneNumber=False":passTransactionPassIdDetails,
   "parkingPassTransId=False, passId=False, parkingOwnerId=True, branchId=False, taxId=False, userId=False, type=False, phoneNumber=False":passTransactionOwnerIdDetails,
   "parkingPassTransId=False, passId=False, parkingOwnerId=False, branchId=True, taxId=False, userId=False, type=False, phoneNumber=False":passTransactionBranchIdDetails,
   "parkingPassTransId=False, passId=False, parkingOwnerId=False, branchId=False, taxId=True, userId=False, type=False, phoneNumber=False":passTransactionTaxIdDetails,
   "parkingPassTransId=False, passId=False, parkingOwnerId=False, branchId=False, taxId=True, userId=False, type=True, phoneNumber=False":passTransactionTaxIdTypeDetails,
   "parkingPassTransId=False, passId=True, parkingOwnerId=False, branchId=False, taxId=False, userId=True, type=False, phoneNumber=False":passTransactionPassUserIdDetails,
   "parkingPassTransId=False, passId=False, parkingOwnerId=False, branchId=False, taxId=False, userId=True, type=True, phoneNumber=False":passTransactionUserIdTypeDetails,
   "parkingPassTransId=False, passId=False, parkingOwnerId=False, branchId=False, taxId=False, userId=True, type=False, phoneNumber=False":passTransactionUserIdDetails,
   "parkingPassTransId=False, passId=True, parkingOwnerId=False, branchId=True, taxId=False, userId=False, type=False, phoneNumber=False":passTransactionBranchIdPassIdDetails,
   "parkingPassTransId=False, passId=False, parkingOwnerId=False, branchId=False, taxId=False, userId=False, type=False, phoneNumber=False":passTransactionDetails,
   "parkingPassTransId=False, passId=False, parkingOwnerId=False, branchId=False, taxId=False, userId=False, type=True, phoneNumber=True":passTransactionPhoneNumberTypeDetails
   
}

@passTransactionRouter.get('')
async def parkingPassTransaction(parkingPassTransId:Optional[int]=Query(None),passId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),taxId:Optional[int]=Query(None),userId:Optional[int]=Query(None),type:Optional[str]=Query(None),phoneNumber:Optional[str]=Query(None),db:Cursor = Depends(get_cursor)):
    try:
        st = f"parkingPassTransId={True if parkingPassTransId else False}, passId={True if passId else False}, parkingOwnerId={True if parkingOwnerId else False}, branchId={True if branchId else False}, taxId={True if taxId else False}, userId={True if userId else False}, type={True if type else False}, phoneNumber={True if phoneNumber else False}"
        return await parkingPassDict[st](parkingPassTransId,passId, parkingOwnerId, branchId, taxId, userId, type, phoneNumber,db)
    except Exception as e:
        print("Exception as parkingPassTransaction ",str(e))
        return {
            "statusCode": 0,
            "response":"Server Error"
            
        }

@passTransactionRouter.post('')
async def postPassTransaction(request:schemas.PostPassTransaction,db:Cursor = Depends(get_cursor)):
    try:
        data=[]
        mailData=[]
        for i in request.passTransactionDetails:
            dic={}
            mailDic={}
            taxPercentage=await getPassTransactionTaxId(i.taxId)
            if taxPercentage:
                tax=((i.totalAmount * taxPercentage.get('taxPercentage')) / 100)
                taxName=taxPercentage.get('taxName')
            else:
                tax=0
                taxName=None
            parkingName = redis_client.hget('parkingOwnerMaster', i.parkingOwnerId)
            branchName = redis_client.hget('branchMaster', i.branchId)
            vehicleDetails=redis_client.hget('vehicleConfigMaster', i.vehicleType)
            vehicleTypeName,vehicleImageUrl=tuple(json.loads(vehicleDetails.decode("utf-8")).values()) if vehicleDetails else None
            parkingName=parkingName.decode("utf-8") if parkingName else None
            branchName=branchName.decode("utf-8") if branchName else None
            await db.execute(f"""INSERT INTO passTransaction(passId,parkingOwnerId,parkingName,branchId,branchName,userId,phoneNumber,vehicleType,vehicleTypeName,vehicleImageUrl,validStartDate,validEndDate,
									validStartTime,validEndTime,amount,tax,totalAmount,taxId,taxName,paymentStatus,paymentType,walletCash,cancellationStatus,refundStatus,cancellationCharges,refundAmt,cancellationReason,transactionId,bankName,bankReferenceNumber,offerId,offerAmount,activeStatus,createdBy,createdDate)
                                VALUES(?,?,?,?,?,?,?,?,?,?,getdate(),(SELECT CAST((SELECT CONVERT(DATETIME,(SELECT Top 1 pc.noOfDays FROM parkingPassConfig AS pc WHERE pc.parkingPassConfigId={i.passId}))+GETDATE())AS date)AS DATE),(SELECT CONVERT (TIME, CURRENT_TIMESTAMP)),(SELECT CAST((SELECT CONVERT(DATETIME,(SELECT Top 1 pc.noOfDays FROM parkingPassConfig AS pc WHERE pc.parkingPassConfigId={i.passId}))+(SELECT Format(GETDATE(),'hh:mm:ss tt') as [Time]))AS time)AS TIME),?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,GETDATE())""",
                                (i.passId,
                                i.parkingOwnerId,
                                parkingName,
                                i.branchId,
                                branchName,
                                i.userId,
                                i.phoneNumber,
                                i.vehicleType,
                                vehicleTypeName,
                                vehicleImageUrl,
                                i.totalAmount - tax,
                                tax,
                                i.totalAmount,
                                i.taxId,
                                taxName,
                                i.paymentStatus,
                                i.paymentType,
                                i.walletCash,
                                i.cancellationStatus,
                                i.refundStatus,
                                i.cancellationCharges,
                                i.refundAmt,
                                i.cancellationReason,
                                i.transactionId,
                                i.bankName,
                                i.bankReferenceNumber,
                                i.offerId,
                                i.offerAmount,
                                i.activeStatus,
                                i.createdBy
                                ))
            if db.rowcount>=1:
                await db.execute(f"""SELECT TOP 1 pt.parkingPassTransId,pt.validStartDate,pt.validEndDate ,pc.passType
                                    FROM passTransaction AS pt
                                    INNER JOIN parkingPassConfig as pc
                                    ON pc.parkingPassConfigId=pt.passId
                                    WHERE pt.passId={i.passId} AND pt.branchId={i.branchId}
                                    AND pt.parkingOwnerId={i.parkingOwnerId} AND pt.vehicleType={i.vehicleType} ORDER BY parkingPassTransId DESC """)
                row = await db.fetchone()
                dic.update({"passTransactionId":row[0]})
                mailDic.update({"userId":i.userId,
                                "passType":row[3],
                                "parkingName":parkingName,
                                "validStartDate":row[1],
                                "validEndDate":row[2]})
                data.append(dic)  
                mailData.append(mailDic)
        await db.commit()    
        if data:
            passTransaction.delay(mailData)
            return{"statusCode":1,"response":'Data Added Successfully',"parkingPassTransId":data}
               
        else:
            return{"statusCode":0,"response":'Data Not Added'}
        # await db.execute(f"""EXEC[dbo].[postPassTransaction]
        #                             @passTransactionDetailsJson=?
        #                             """,
        #                             (json.dumps(r,indent=4, sort_keys=True, default=str)))
        # row=await db.fetchone()
        # await db.commit()
        # await publish(queueName='notificationService', message = {
        #             'action':'After Getting Pass',
        #             'body':{
        #                 'emailId': '',
        #                 'phoneNo': '',
        #                 'passType':'P',
        #                 'parkingName':'Hosur Parking',
        #                 'userName':'dhana',
        #                 'fromDate':'2022-08-03',
        #                 'toDate':'2022-08-05',
        #                 'link':'http://prematix.tech/summaryPage'
        #             }
        #         })
        
        # return{"statusCode":int(row[1]),"response":row[0]}     

    except Exception as e:
        print("Exception as postPassTransaction ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@passTransactionRouter.delete('')
async def deletePassTransaction(activeStatus:str,parkingPassTransId:int,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE passTransaction SET activestatus=? WHERE parkingPassTransId=?",activeStatus,parkingPassTransId)
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
        print("Exception as deletePassTransaction ",str(e))
        return{"statusCode":0,"response":"Server Error"}