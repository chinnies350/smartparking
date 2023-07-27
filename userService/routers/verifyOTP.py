from sqlite3 import Cursor
from fastapi.routing import APIRouter
from fastapi import Depends
from routers.config import get_cursor
from dotenv import load_dotenv
import schemas
from random import randint
from task import verifyOTPData
import json


load_dotenv()

verifyOTPRouter = APIRouter(prefix='/verifyOTP')

@verifyOTPRouter.post('')
async def postVerifyOTP(request:schemas.VerifyOTP,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[verifyOTP] ?""",(request.username))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            OTP = randint(100000, 999999)
            verifyOTPData.delay(json.loads(row[2]),OTP)
            return{"statusCode":int(row[1]),"response":row[0],'OTP':OTP}
        else:
            return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postVerifyOTP ",str(e))
        return{"statusCode":0,"response":"Server Error"}