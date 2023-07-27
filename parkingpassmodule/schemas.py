from pydantic import BaseModel
from typing import Optional,List
from fastapi import Query
from datetime import datetime,date,time



class ParkingPassConfig(BaseModel):
    parkingOwnerId:int
    branchId:int
    passCategory:str
    passType:str
    noOfDays:int
    parkingLimit:Optional[int]=Query(0)
    totalAmount:float
    taxId:int
    vehicleType:int
    remarks:Optional[str]=Query(None)
    activeStatus:str
    createdBy:int

class PutParkingPassConfig(BaseModel):
    parkingPassConfigId:int
    parkingOwnerId:int
    branchId:int
    passCategory:str
    passType:str
    noOfDays:int
    parkingLimit:int
    totalAmount:float
    taxId:int
    vehicleType:int
    remarks:str
    activeStatus:str
    updatedBy:int

class PassTransaction(BaseModel):
    passId:int
    parkingOwnerId:int
    branchId:int
    userId:Optional[int]=Query(None)
    phoneNumber:Optional[str]=Query(None)
    vehicleType:int
    totalAmount:float
    taxId:int
    paymentStatus:str
    paymentType:int
    walletCash:Optional[float]=Query(None)
    cancellationStatus:Optional[str]=Query(None)
    refundStatus:Optional[str]=Query(None)
    cancellationCharges:Optional[float]=Query(None)
    refundAmt:Optional[float]=Query(None)
    cancellationReason:Optional[str]=Query(None)
    transactionId:Optional[str]=Query(None)
    bankName:Optional[str]=Query(None)
    bankReferenceNumber:Optional[str]=Query(None)
    offerId:Optional[int]=Query(None)
    offerAmount:Optional[float]=Query(None)
    activeStatus:str
    createdBy:int

class PostPassTransaction(BaseModel):
    passTransactionDetails:List[PassTransaction]