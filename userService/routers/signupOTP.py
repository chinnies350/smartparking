from sqlite3 import Cursor
from fastapi.routing import APIRouter
from fastapi import Depends
from routers.config import get_cursor
from dotenv import load_dotenv
import schemas
from random import randint
from task import signUpOTPData
import json

load_dotenv()

signupOTPRouter = APIRouter(prefix='/signupOtp')

@signupOTPRouter.post('')
async def postSignupOTP(request:schemas.signupOtp,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[signupOtp] ?""",(request.username))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            OTP = randint(1000, 9999)
            signUpOTPData.delay(request.username,OTP,row[2])
            return{"statusCode":int(row[1]),"response":row[0],'OTP':OTP}
        else:
            return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as postSignupOTP ",str(e))
        return{"statusCode":0,"response":"Server Error"}