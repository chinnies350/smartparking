from pydantic import BaseModel
from typing import Optional,List
from fastapi import Query
from datetime import datetime,date,time


class OfferRules(BaseModel):
    offerRule:str
    ruleType:int
    activeStatus:str

class OfferMaster(BaseModel):
    offerTypePeriod:str
    offerHeading:str
    offerDescription:str
    offerCode:str
    offerImageUrl:str
    fromDate:date
    toDate:date
    fromTime:time
    toTime:time
    offerType:str
    offerValue:float
    minAmt:float
    maxAmt:float
    noOfTimesPerUser:int
    activeStatus:str
    createdBy:int
    offerRulesDetails:Optional[List[OfferRules]] = Query(None)

class PutOfferRules(BaseModel):
    offerRuleId:Optional[int] = Query(None)
    offerId:int
    offerRule:str
    ruleType:int
    activeStatus:str

class PutOfferMaster(BaseModel):
    offerId:int
    offerTypePeriod:str
    offerHeading:str
    offerDescription:str
    offerCode:str
    offerImageUrl:str
    fromDate:date
    toDate:date
    fromTime:time
    toTime:time
    offerType:str
    offerValue:float
    minAmt:float
    maxAmt:float
    noOfTimesPerUser:int
    activeStatus:str
    updatedBy:int
    offerRulesDetails:Optional[List[PutOfferRules]]=Query(None)



class PostOfferRulesDetails(BaseModel):
    offerId:int
    offerRulesDetails:List[OfferRules]

class PutOfferRulesDetails(BaseModel):
    offerRulesDetails:List[PutOfferRules]


class OfferMapping(BaseModel):
    parkingOwnerId:int
    branchId:int
    offerId:int
    activeStatus:str
    createdBy:int