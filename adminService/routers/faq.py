import json
from sqlite3 import Cursor
from fastapi.routing import APIRouter
from routers.config import get_cursor
from fastapi import Depends
from typing import Optional
from fastapi import Query
import schemas
import os
import routers

faqRouter = APIRouter(prefix='/faq')

async def getOfferDetails(offerId):
    try:
        response = await routers.client.get(f"{os.getenv('OFFER_SERVICE_URL')}/offerMaster?offerId={offerId}")
        response = json.loads(response.text)
        if response['statusCode'] == 1:
            return response['response']
        return ""
    except Exception as e:
        print("Exception as getOfferDetails ",str(e))
        return ""

async def modifiedDataOfferDetails(offerId, dic):
    dic['offerDetails'] = await getOfferDetails(offerId)

async def getDetailsBasedOnFaqId(faqId, db):
    
    try:
        data =[]
        await db.execute(f"""SELECT CAST((SELECT faq.faqId,faq.offerId,faq.question,faq.answer,faq.questionType,faq.activeStatus
                            FROM faq
                            WHERE faqId=?
                            FOR JSON PATH) AS VARCHAR(MAX))""",(faqId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                
                if dic['offerId']:
                    await modifiedDataOfferDetails(dic['offerId'],dic)
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
        print("Exception as getDetailsBasedOnFaqId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnaAtiveStatus(activeStatus, db):
    
    try:
        data =[]
        await db.execute(f"""SELECT CAST((SELECT faq.faqId,faq.offerId,faq.question,faq.answer,faq.questionType,faq.activeStatus
                            FROM faq
                            WHERE activeStatus=?
                            FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                if dic['offerId']:
                    await modifiedDataOfferDetails(dic['offerId'],dic)
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
        print("Exception as getDetailsBasedOnaAtiveStatus ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnActiveQuestionType(activeStatus,questionType, db):
    data =[]
    try:
        await db.execute(f"""SELECT CAST((SELECT faq.faqId,faq.offerId,faq.question,faq.answer,faq.questionType,faq.activeStatus
                            FROM faq
                            WHERE activeStatus=? AND questionType=?
                            FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus,questionType))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                if dic['offerId']:
                    await modifiedDataOfferDetails(dic['offerId'],dic)
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
        print("Exception as getDetailsBasedOnActiveQuestionType ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getDetailsBasedOnOfferId(offerId, db):
    data =[]
    try:
        await db.execute(f"""SELECT CAST((SELECT faq.faqId,faq.offerId,faq.question,faq.answer,faq.questionType,faq.activeStatus
                            FROM faq
                            WHERE offerId=?
                            FOR JSON PATH) AS VARCHAR(MAX))""",(offerId))
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                if dic['offerId']:
                    await modifiedDataOfferDetails(dic['offerId'],dic)
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
        print("Exception as getDetailsBasedOnOfferId ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def getFaqDetails(db):
    data =[]
    try:
        await db.execute(f"""SELECT CAST((SELECT faq.faqId,faq.offerId,faq.question,faq.answer,faq.questionType,faq.activeStatus
                            FROM faq
                            
                            FOR JSON PATH) AS VARCHAR(MAX))""")
        row = await db.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                dic = {}
                dic.update(i)
                if dic.get('offerId'):
                    await modifiedDataOfferDetails(dic['offerId'],dic)
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
        print("Exception as getFaqDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

@faqRouter.get('')
async def getFaq(faqId:Optional[int]=Query(None),activeStatus:Optional[str]=Query(None),offerId:Optional[int]=Query(None),questionType:Optional[str]=Query(None), db: Cursor = Depends(get_cursor)):
    try:
        if faqId:
            return await getDetailsBasedOnFaqId(faqId,db)
        elif activeStatus and questionType==None:
            return await getDetailsBasedOnaAtiveStatus(activeStatus, db)
        elif activeStatus and questionType:
            return await getDetailsBasedOnActiveQuestionType(activeStatus,questionType, db)
        elif offerId:
            return await getDetailsBasedOnOfferId(offerId, db)
        else:
            return await getFaqDetails(db)
    except Exception as e:
        print("Exception as getFaq ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


@faqRouter.post('')
async def postFaq(request:schemas.Faq,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[postFaq]
                                        @offerId =?,
                                        @question =?,
                                        @answer =?,
                                        @questionType =?,
                                        @activeStatus =?,
                                        @createdBy =?
                                        """,
                                            (request.offerId,
                                            request.question,
                                            request.answer,
                                            request.questionType,
                                            request.activeStatus,
                                            request.createdBy
                                            ))
        row=await db.fetchall()
        await db.commit()
        return{"statusCode":int(row[0][1]),"response":row[0][0]}

    except Exception as e:
        print("Exception as postFaq ",str(e))
        return{"statusCode":0,"response":"Server Error"}

@faqRouter.put('')
async def putFaq(request:schemas.PutFaq,db:Cursor = Depends(get_cursor)):
    try:
        await db.execute(f"""EXEC [dbo].[putFaq]
                                                @offerId =?,
                                                @question =?,
                                                @answer =?,
                                                @questionType =?,
                                                @updatedBy =?,
                                                @faqId=?
                                                """,
                                            (
                                            request.offerId ,
                                            request.question,
                                            request.answer,
                                            request.questionType,
                                            request.updatedBy,
                                            request.faqId
                                            ))
        row=await db.fetchone()
        await db.commit()
        return{"statusCode":int(row[1]),"response":row[0]}

    except Exception as e:
        print("Exception as putFaq ",str(e))
        return{"statusCode":0,"response":"Server Error"}


@faqRouter.delete('')
async def deleteFaq(faqId:int,activeStatus:str,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE faq SET activeStatus=? WHERE faqId=?",activeStatus,faqId)
        await db.commit()
        if result.rowcount>=1:
            if activeStatus=='D':
                return {
                         "statusCode": 1,
                         "response": "Deactivated successfully"}
            else:
                return {"statusCode": 1,
                        "response": "Activated successfully"}
        else:
            return { "statusCode": 0,
                    "response": "Data Not Found"}

    except Exception as e:
        print("Exception as deleteFaq ",str(e))
        return{"stausCode":0, "response":"Server Error"}