from sqlite3 import Cursor
from fastapi.routing import APIRouter
from fastapi import Depends
from routers.config import get_cursor
from dotenv import load_dotenv
import schemas
from task import forgotMailData
import json


load_dotenv()

forgotPasswordRouter = APIRouter(prefix='/forgotpassword')

@forgotPasswordRouter.put('')
async def putForgotPassword(request:schemas.Forgotpassword,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[Passwordrecovery]?,?""",(request.password,request.username))
        row=await db.fetchone()
        await db.commit()
        if int(row[1])==1:
            forgotMailData.delay(json.loads(row[2]))
            return{"statusCode":int(row[1]),"response":row[0]}
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putForgotPassword ",str(e))
        return{"statusCode":0,"response":"Server Error"}