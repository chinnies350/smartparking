from dbm import dumb
from difflib import Match
import json
from sys import prefix
from fastapi.routing import APIRouter
from typing import Optional
from fastapi import Query
from routers.eventsServer import publish
import routers
from fastapi import Depends
from routers.config import get_cursor
from aioodbc.cursor import Cursor
import os
import schemas
import datetime
from json import dumps
from task import postParkingName
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/admin",tags=['admin'])
@router.post('')
async def postadmin(request:schemas.PostAdmin,db:Cursor=Depends(get_cursor)):
    try:
        url = f"{os.getenv('USER_SERVICE_URL')}/userMaster"
        data={'userName':request.userName,
              'password':request.password,
              'emailId':request.emailId,
              'phoneNumber':request.phoneNumber,
              'approvalStatus':request.approvalStatus,
              'userRole':request.userRole,
              'imageUrl':request.imageUrl,
              'activeStatus':request.activeStatus,
              'createdBy':request.createdBy}
        response = await routers.client.post(url,json=data)    
        var=json.loads(response.text)
       
        if var['userId']!=None:
            await db.execute(f"""EXEC [dbo].[postParkingOwnerMaster]
                                        @userId=?,
                                        @parkingName=?,
                                        @shortName=?,
                                        @founderName=?,
                                        @logoUrl=?,
                                        @websiteUrl=?,
                                        @gstNumber=?,
                                        @placeType=?,
                                        @activeStatus=?,
                                        @createdBy=?
                                        """,
                                        (var['userId'],
                                        request.parkingName,
                                        request.shortName,
                                        request.founderName,
                                        request.logoUrl,
                                        request.websiteUrl,
                                        request.gstNumber,
                                        request.placeType,
                                        request.activeStatus,
                                        request.createdBy))
            rows=await db.fetchone()
            await db.commit()
            if int(rows[1])==1:
                postParkingName.delay(int(rows[2]),request.parkingName)
                return{
                    "statusCode":int(rows[1]),
                    "response":rows[0]
                }
            return{
                    "statusCode":int(rows[1]),
                    "response":rows[0]
                }
        else:
            return{
            "statusCode": 0,
            "response": "Data Not Added"
        }
    except Exception as e:
        print("Exception as postadmin ",str(e))
        return{
        "statusCode": 0,
        "response":"Server Error"  
        } 
    
