from pydantic import BaseModel
from typing import Optional
from fastapi import Query
from datetime import datetime,date,time

class SubscriptionMaster(BaseModel):
    subscriptionName:str
    validity:int
    offerType:str
    offerValue:float
    parkingLimit:Optional[int]=Query(None)
    rules:str
    taxId:int
    # amount:Optional[float]=Query(None)
    # tax:float
    totalAmount:float
    validityFrom:Optional[datetime]=Query(None)
    validityTo:Optional[datetime]=Query(None)
    activeStatus:str
    createdBy:int
    

class PutSubscriptionMaster(BaseModel):
    subscriptionName:str
    validity: int
    offerType:str
    offerValue:float
    parkingLimit:Optional[int]=Query(None)
    rules:str
    totalAmount:float
    validityFrom:Optional[datetime]=Query(None)
    validityTo:Optional[datetime]=Query(None)
    updatedBy:int
    activeStatus:str
    subscriptionId:int
    taxId:int

class UserSubscription(BaseModel):
    userId:int
    subscriptionId:int
    validityFrom:date
    validityTo:date
    actualCount:Optional[int]=Query(None)
    remainingCount:Optional[int]=Query(None)
    taxId:int
    amount:Optional[float]=Query(None)
    tax:float
    totalAmount:float
    passType:Optional[str]=Query(None)
    

class PutUserSubscription(BaseModel):
    passId:int
    userId:int
    subscriptionId:int
    validityFrom:date
    validityTo:date
    actualCount:Optional[int]=Query(None)
    remainingCount:Optional[int]=Query(None)
    taxId:int
    amount:Optional[float]=Query(None)
    tax:float
    totalAmount:float
    passType:Optional[str]=Query(None)
    