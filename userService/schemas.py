from pydantic import BaseModel
from typing import Optional,List
from fastapi import Query
from datetime import datetime,date,time
from xmlrpc.client import boolean

class UserMaster(BaseModel):
    parkingOwnerId:Optional[int]=Query(None)
    branchId:Optional[int]=Query(None)
    blockId:Optional[int]=Query(None)
    floorId:Optional[int]=Query(None)
    userName:str
    password:Optional[str]=Query(None)
    emailId:Optional[str]=Query(None)
    phoneNumber:Optional[str]=Query(None)
    alternatePhoneNumber:Optional[str]
    mainContactName:Optional[int]=Query(None)
    address : Optional[str]
    city : Optional[str]
    district : Optional[str]
    state : Optional[str]
    pincode : Optional[int]
    imageUrl:Optional[str]
    DOJ:Optional[datetime]
    empType:Optional[int]
    userRole:str
    empDesignation: Optional[int]=Query(None)
    approvalStatus : Optional[str]
    activeStatus : str
    walletAmt:Optional[float]=Query(0)
    loyaltyPoints:Optional[int]=Query(None)
    createdBy : Optional[int]=Query(None)
    shiftId:Optional[int]
    otp: Optional[int]=Query(None)
    registrationToken:Optional[str]=Query(None)

class PutUserMaster(BaseModel):
    parkingOwnerId:Optional[int]
    userId:int
    branchId:Optional[int]
    blockId:Optional[int]
    floorId:Optional[int]
    userName:str
    password:str
    emailId:Optional[str]
    phoneNumber:Optional[str]
    alternatePhoneNumber:Optional[str]
    address : Optional[str]
    city : Optional[str]
    district : Optional[str]
    state : Optional[str]
    pincode : Optional[int]
    imageUrl:Optional[str]
    DOJ:Optional[datetime]
    empType:Optional[int]
    empDesignation: Optional[int]
    updatedBy : Optional[int]
    walletAmt:Optional[float]
    loyaltyPoints:Optional[int]
    shiftId:Optional[int]
    employeeId:Optional[int]
    addressId:Optional[int]

class UpdateRegistrationToken(BaseModel):
    userId:int
    registrationToken:str

class vehicleMaster(BaseModel):
    userId:int
    vehicleName:Optional[str]=Query(None)
    vehicleNumber:str
    vehicleType:int
    vehicleImageUrl:Optional[str]=Query(None)
    documentImageUrl:Optional[str]=Query(None)
    isEV:Optional[boolean]=Query(None)
    chargePinType:Optional[int]=Query(None)

class PutvehicleMaster(BaseModel):
    vehicleId:int
    userId:int
    vehicleName:Optional[str]
    vehicleNumber:str
    vehicleType:int    
    vehicleImageUrl:Optional[str]
    documentImageUrl:Optional[str]
    isEV:Optional[boolean]
    chargePinType:Optional[int]

class UserOffers(BaseModel):
    userId:int
    offerId:int
    fromDate:date
    toDate:date
    fromTime:time
    toTime:time
    activeStatus:str

class UserWallet(BaseModel):
    userId:int
    walletAmt:Optional[float]=Query(None)
    loyaltyPoints:Optional[int]=Query(None)
    status:str
    expiryDate:Optional[datetime] = Query(None)
    creditedDate:datetime
    reasonToCredit:str

class FeedBackMaster(BaseModel):
    parkingOwnerId:int
    branchId:int
    bookingId:int
    feedbackRating:Optional[int]
    feedbackComment:Optional[str]
    createdBy : int

class PutFeedBackMaster(BaseModel):
    FeedbackId:int
    parkingOwnerId:int
    branchId:int
    bookingId:int
    feedbackRating:Optional[int]
    feedbackComment:Optional[str]
    updatedBy : int

class optionDetail(BaseModel):
    optionId:int
    ViewRights:bool
    AddRights:bool
    EditRights:bool
    DeleteRights:bool
    activeStatus:str
    
class MenuOptionAccess(BaseModel):
    parkingOwnerId:int
    userId:int
    moduleId:int
    optionDetails:Optional[List[optionDetail]] = None
    createdBy:int

class PutMenuOptionAccess(BaseModel):
    MenuOptionAccessId:int
    viewRights:bool
    addRights:bool
    editRights:bool
    deleteRights:bool
    activeStatus:str
    updatedBy:Optional[int]

class ListPutMenuOptionAccess(BaseModel):
    menuOptionAccessDetails : List[PutMenuOptionAccess] 


class AddressMaster(BaseModel):
    userId:int
    alternatePhoneNumber:Optional[str]
    address:Optional[str]
    district:Optional[str]
    state:Optional[str]
    city:Optional[str]
    pincode:int
    createdBy:int


class PutAddressMaster(BaseModel):
    addressId:int
    userId:int
    alternatePhoneNumber:str
    address:str
    district:str
    state:str
    city:str
    pincode:int
    updatedBy:int

class Forgotpassword(BaseModel):
    password:str
    username:str

class VerifyOTP(BaseModel):
    username:str

class signupOtp(BaseModel):
    username:str


# class FireBaseNotification(BaseModel):
#     title:str
#     body:str
#     userId:str