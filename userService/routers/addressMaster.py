from fastapi import APIRouter
from typing import Optional
from aioodbc.cursor import Cursor
from fastapi import Depends
from routers.config import get_cursor
import json
from routers import Response
import schemas
from fastapi import Query
from typing import Optional

addressMasterRouter = APIRouter(prefix="/addressMaster",tags=['addressMaster'])


@addressMasterRouter.get('')
async def getAddressDetails(userId: Optional[int]=Query(None),addressId: Optional[int]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[getAddressMaster] ?,?""",(addressId,userId))
        row = await db.fetchone()
        if row[0]:
            return {"statusCode": 1, "response":  json.loads(row[0]) if row[0] != None else []}
        return Response("NotFound")
            
    except Exception as e:
        print("Exception as getAddressDetails ",str(e))
        return {
            'response':"Server Error",
            'statusCode': 0
        }

@addressMasterRouter.post('')
async def postAddressMaster(request:schemas.AddressMaster, db: Cursor = Depends(get_cursor)):
    try:
        # with engine.connect() as cur:
        await db.execute(f"""EXEC [dbo].[postAddressMaster]
                                        @userId =?,
                                        @alternatePhoneNumber =?,
                                        @address =?,
                                        @district =?,
                                        @state =?,
                                        @city =?,
                                        @pincode =?,
                                        @createdBy =?""",
                                        (
                                        request.userId,
                                        request.alternatePhoneNumber,
                                        request.address,
                                        request.district,
                                        request.state,
                                        request.city,
                                        request.pincode,
                                        request.createdBy))
        rows=await db.fetchone()
        return{"statusCode":int(rows[0][1]),"response":rows[0][0]}
    except Exception as e:
        print("Exception as postAddressMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@addressMasterRouter.put('')
async def putAddressMaster(request:schemas.PutAddressMaster, db: Cursor = Depends(get_cursor)):
    try:
        # with engine.connect() as cur:
        await db.execute(f"""EXEC [dbo].[putAddressMaster]
                                        @addressId=?,
                                        @userId =?,
                                        @alternatePhoneNumber =?,
                                        @address =?,
                                        @district =?,
                                        @state =?,
                                        @city =?,
                                        @pincode =?,
                                        @updatedBy =?""",
                                        (
                                        request.addressId,
                                        request.userId,
                                        request.alternatePhoneNumber,
                                        request.address,
                                        request.district,
                                        request.state,
                                        request.city,
                                        request.pincode,
                                        request.updatedBy))
        rows=await db.fetchone()
        return{"statusCode":int(rows[0][1]),"response":rows[0][0]}
    except Exception as e:
        print("Exception as putAddressMaster ",str(e))
        return{"statusCode":0,"response":"Server Error"}


