from pydantic import BaseModel
from typing import Optional,List
from fastapi import Query
from datetime import datetime,date,time
from xmlrpc.client import boolean

class PostMessageTemplates(BaseModel):
    messageHeader:str
    subject:str
    messageBody:str
    templateType:str
    peid:Optional[str]=Query(None)
    tpid:Optional[str]=Query(None)
    createdBy:int
    
class PutMessageTemplates(BaseModel):
    uniqueId:int
    messageHeader:str
    subject:str
    messageBody:str
    templateType:str
    peid:Optional[str]=Query(None)
    tpid:Optional[str]=Query(None)
    updatedBy:int

class SendNotification(BaseModel):
    type: Optional[str] = Query(None)
    emailId: Optional[str] = Query(None)
    mobileNo:Optional[str]=Query(None)
    link:Optional[str]=Query(None)

class FireBaseNotification(BaseModel):
    title:str
    body:str
    userId:str