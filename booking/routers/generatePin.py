from sqlite3 import Cursor
from fastapi.routing import APIRouter
from fastapi import Depends
from routers.config import get_cursor
from dotenv import load_dotenv


load_dotenv()

generatePinRouter = APIRouter(prefix='/generatePin')

@generatePinRouter.get('')
async def generatePin(db: Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[generatePin]""")
        rows=await db.fetchone()
        await db.commit()
        if rows[0]!=None:
            return {"statusCode": 1,"response":rows[0]}
        else:
            return {
                    "statusCode":0,
                    "response":"Data Not Found"
                    }
    except Exception as e:
        print("Exception as generatePin ",str(e))
        return{"statusCode":0,"response":"Server Error"}