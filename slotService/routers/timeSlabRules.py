from fastapi import Query
from fastapi.routing import APIRouter
from typing import Optional
from routers.config import get_cursor
from fastapi import Depends
from aioodbc.cursor import Cursor
from dotenv import load_dotenv
import schemas


load_dotenv()

timeSlabRulesRouter=APIRouter(prefix="/timeSlabRules")

@timeSlabRulesRouter.post('')
async def postTimeSlabRules(request:schemas.TimeSlabRules,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postTimeSlabRules]
                                                @priceId=?,
                                                @fromDate=?,
                                                @toDate=?,
                                                @activeStatus=?,
                                                @createdBy=?
                                                """,
                                            (request.priceId,
                                            request.fromDate,
                                            request.toDate,
                                            request.activeStatus,
                                            request.createdBy
                                            ))
        row=await db.fetchall()
        await db.commit()
        return{"statusCode":int(row[0][1]),"response":row[0][0]}

    except Exception as e:
        print("Exception as postTimeSlabRules ",str(e))
        return{"statusCode":0,"response":"Server Error"}