from pydantic import BaseModel
from datetime import datetime,date,time
from fastapi import Query
from typing import List, Optional
from xmlrpc.client import boolean

class PostparkingOwner(BaseModel):
    userId:int
    parkingName:str
    shortName:str
    founderName:str
    logoUrl:Optional[str]=Query(None)
    websiteUrl:Optional[str]=Query(None)
    gstNumber:Optional[str]=Query(None)
    placeType:Optional[str]=Query(None)
    activeStatus:str
    createdBy:int

class PutParkingOwnerMaster(BaseModel):
      parkingOwnerId:int
      userId:int
      parkingName:str
      shortName:str
      founderName:str
      logoUrl:str
      websiteUrl:str
      gstNumber:str
      placeType:str
      updatedBy:int

class shiftMaster(BaseModel):
    parkingOwnerId:int
    branchId:int
    shiftName:int
    startTime:time
    endTime:time
    breakStartTime:Optional[time]=Query(None)
    breakEndTime:Optional[time]=Query(None)
    gracePeriod:Optional[int]=Query(None)
    activeStatus:str
    createdBy:int

class putshiftMaster(BaseModel):
    shiftId:int
    parkingOwnerId:int
    branchId:int
    shiftName:int
    startTime:time
    endTime:time
    breakStartTime:Optional[time]=Query(None)
    breakEndTime:Optional[time]=Query(None)
    gracePeriod:Optional[int]=Query(None)
    activeStatus:str
    updatedBy:int

class BlockMaster(BaseModel):
    parkingOwnerId:int
    branchId:int
    blockName:str
    activeStatus:str
    approvalStatus:str
    createdBy:int

class PutBlockMaster(BaseModel):
    blockId:int
    parkingOwnerId:int
    branchId:int
    blockName:str
    approvalStatus:str
    updatedBy:int

class PostAdmin(BaseModel):
    userName:str
    password:str
    emailId:Optional[str]=Query(None)
    phoneNumber:Optional[str]=Query(None)
    approvalStatus:Optional[str]=Query(None)
    userRole:str
    imageUrl:Optional[str]=Query(None)
    activeStatus : str
    createdBy:Optional[int]=Query(None)
    # userId:int
    parkingName:str
    shortName:str
    founderName:str
    logoUrl:Optional[str]=Query(None)
    websiteUrl:Optional[str]=Query(None)
    gstNumber:Optional[str]=Query(None)
    placeType:Optional[str]=Query(None)

class BranchWorkingHrsDetails(BaseModel):
    workingDay:Optional[str]
    fromTime:time
    toTime:time
    isHoliday:Optional[boolean]

class BranchImageMasterDetails(BaseModel):
    imageUrl:str


class BranchMaster(BaseModel):
    parkingOwnerId:int
    branchName:str
    shortName:str
    latitude:float
    longitude:float
    address1:Optional[str]=Query(None)
    address2:Optional[str]=Query(None)
    district:Optional[str]=Query(None)
    state:Optional[str]=Query(None)
    city:Optional[str]=Query(None)
    pincode:int
    phoneNumber:str
    alternatePhoneNumber:Optional[str]=Query(None)
    emailId:Optional[str]=Query(None)
    licenseNo:str
    licensePeriodFrom:date
    licensePeriodTo:date
    license:str
    document1:Optional[str]=Query(None)
    document2:Optional[str]=Query(None)
    multiBook:str
    activeStatus:str
    approvalStatus:str
    onlineBookingAvailability:str
    isPayBookAvailable:str
    isBookCheckInAvailable:str
    isPayAtCheckoutAvailable:str
    isPayLaterAvaialble:str
    advanceBookingHourOrDayType : Optional[str]=Query(None)
    advanceBookingHourOrDay :Optional[int]=Query(None)
    advanceBookingCharges :Optional[float]=Query(None)
    minHour :Optional[int]=Query(None)
    maxHour :Optional[int]=Query(None)
    minDay :Optional[int]=Query(None)
    maxDay :Optional[int]=Query(None)
    createdBy:int
    branchWorkingHrsDetails:Optional[List[BranchWorkingHrsDetails]] = None
    branchImageMasterDetails:Optional[List[BranchImageMasterDetails]] = None

class BranchWorkingHrsDetail(BaseModel):
    uniqueId:int
    workingDay:str
    fromTime:time
    toTime:time
    isHoliday:boolean
class PutBranchImageMaster(BaseModel):
    imageId:int
    imageUrl:str


class PutBranchMaster(BaseModel):
    branchId:int
    parkingOwnerId:int
    branchName:str
    shortName:str
    latitude:float
    longitude:float
    address1:str
    address2:str
    district:str
    state:str
    city:str
    pincode:int
    phoneNumber:str
    alternatePhoneNumber:str
    emailId:str
    licenseNo:str
    licensePeriodFrom:date
    licensePeriodTo:date
    license:str
    document1:str
    document2:str
    multiBook:str
    approvalStatus:str
    onlineBookingAvailability:str
    isPayBookAvailable:str
    isBookCheckInAvailable:str
    isPayAtCheckoutAvailable:str
    isPayLaterAvaialble:str
    advanceBookingHourOrDayType : Optional[str]=Query(None)
    advanceBookingHourOrDay :Optional[int]=Query(None)
    advanceBookingCharges :Optional[float]=Query(None)
    minHour :Optional[int]=Query(None)
    maxHour :Optional[int]=Query(None)
    minDay :Optional[int]=Query(None)
    maxDay :Optional[int]=Query(None)
    updatedBy:int
    branchWorkingHrs:Optional[List[BranchWorkingHrsDetail]]=Query(None)
    branchImageMasterDetails:Optional[List[PutBranchImageMaster]]=Query(None)

class BranchWorkingHrs(BaseModel):
    branchId:int
    parkingOwnerId:int
    workingDay:str
    fromTime:time
    toTime:time
    isHoliday:boolean
    createdBy:int

class PutBranchWorkingHrs(BaseModel):
    uniqueId:int
    branchId:int
    parkingOwnerId:int
    workingDay:str
    fromTime:time
    toTime:time
    isHoliday:boolean
    updatedBy:int

class PrintingInstructionsConfig(BaseModel):
    parkingOwnerId:int
    branchId:int
    instructionType:str
    instructions:str
    createdBy:int

class PutPrintingInstructionsConfig(BaseModel):
    parkingOwnerId:int
    branchId:int
    instructionType:str
    instructions:str
    updatedBy:int
    uniqueId:int

class instructionsDetails(BaseModel):
    instructions:str

class PrintingInstructionsConfig1(BaseModel):
    parkingOwnerId:int
    branchId:int
    instructionType:str
    instructionsDetails:List[instructionsDetails]
    createdBy:int

class CancellationRules(BaseModel):
    type:str
    duration:int
    noOfTimesPerUser:int
    cancellationCharges:float
    activeStatus:str
    createdBy:int

class PutCancellationRules(BaseModel):
    type:str
    duration:int
    noOfTimesPerUser:int
    cancellationCharges:float
    updatedBy:int
    uniqueId:int

class EmployeeMaster(BaseModel):
    parkingOwnerId:int
    branchId:int
    blockId:int
    floorId:int
    userId:int
    DOJ:datetime
    empType:int
    empDesignation:int
    shiftId:int
    createdBy:int

class PutemployeeMaster(BaseModel):
    employeeId:int
    parkingOwnerId:int
    branchId:int
    blockId:int
    floorId:int
    userId:int
    DOJ:datetime
    empType:int
    empDesignation:int
    shiftId:int
    updatedBy:int

class PaymentUPIDetails(BaseModel):
    name:Optional[str]=Query(None)
    phoneNumber:Optional[str]=Query(None)
    UPIId:str
    branchId :Optional[int]=Query(None)
    merchantId :str
    merchantCode :str
    mode: Optional[str] = Query(None)
    orgId: Optional[str] = Query(None)
    sign : Optional[str] = Query(None)
    url: Optional[str]= Query(None)
    activeStatus:str
    createdBy :int

class PutPaymentUPIDetails(BaseModel):
    name:str
    phoneNumber:str
    UPIId:str
    branchId:int
    merchantId:str
    merchantCode:str
    mode: Optional[str] = Query(None)
    orgId: Optional[str] = Query(None)
    sign : Optional[str] = Query(None)
    url: Optional[str]= Query(None)
    updatedBy:int
    paymentUPIDetailsId:int

   