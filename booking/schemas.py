from pydantic import BaseModel
from datetime import time, date,datetime
from typing import List, Optional
from fastapi import Query

class PostBooking(BaseModel):
    parkingOwnerId: int
    branchId : int
    blockId : int
    floorId: int
    userId: int
    slotId: int
    booking: str
    pinNo: str
    loginType: str
    bookingDurationType: str
    fromTime: Optional[datetime]
    toTime: Optional[datetime]
    fromDate: Optional[datetime]
    toDate: Optional[datetime]
    accessories: str
    bookingType: str
    subscriptionId: Optional[int]
    totalAmount: Optional[float]
    paidAmount: Optional[float]
    paymentStatus: str
    paymentType: str
    offerId: Optional[int]
    createdBy: int


class PostVehicleHeader(BaseModel):
    bookingIdType:str
    bookingPassId:int
    # vehicleNumberType:Optional[int]=Query(None)
    vehicleType:int
    vehicleNumber:str
    inTime:datetime
    vehicleStatus:str
    createdBy:int

class PutVehicleHeader(BaseModel):
    vehicleHeaderId:int
    inTime:Optional[time]=Query(None)
    outTime:Optional[time]=Query(None)
    updatedBy:int
    vehicleStatus:str
    slotId:Optional[int]
    paidAmount:Optional[float]
    paymentType:Optional[int]
    transactionId :Optional[str]=Query(None)
    bankName :Optional[str]=Query(None)
    bankReferenceNumber:Optional[str]=Query(None)

class PostExtraFees(BaseModel):
    bookingPassId :int
    bookingIdType:str
    count:int
    extraFee: float
    extraFeesDetails: Optional[str]=Query(None)
    createdBy: int

class PutPaymentStatus(BaseModel):
    paymentStatus:str
    bookingId:int
    transactionId:str
    bankName:str
    bankReferenceNumber:str

class PutBookingDateTimeExtend(BaseModel):
    bookingDurationType:str
    toTime:Optional[time]=Query(None)
    toDate:Optional[date]=Query(None)
    taxAmount:Optional[float]=Query(0)
    paidAmount:Optional[float]=Query(None)
    totalAmount:float
    bookingId:int
    vehicleHeaderId:Optional[int]=Query(None)
    updatedBy:int
    vehicleStatus:Optional[str]=Query(None)
    slotId:Optional[int] = Query(None)
    paymentType:Optional[int]=Query(None)
    transactionId :Optional[str]=Query(None)
    bankName :Optional[str]=Query(None)
    bankReferenceNumber:Optional[str]=Query(None)

class PutBookingPaidAmount(BaseModel):
    paidAmount:float
    bookingId:int
    updatedBy:int
    paymentType:int
    paymentStatus:Optional[str]=Query(None)
    transactionId :Optional[str]=Query(None)
    bankName :Optional[str]=Query(None)
    bankReferenceNumber:Optional[str]=Query(None)

class PostExtraFeatures(BaseModel):
    bookingPassId: int
    bookingIdType: str
    floorFeaturesId :int
    count:int
    extraDetail:Optional[str]=Query(None)

class VehicleHeader(BaseModel):
    # vehicleNumberType:Optional[int]=Query(None)
    vehicleType:int
    vehicleNumber:str
    inTime:Optional[datetime]=Query(None)
    outTime:Optional[datetime]=Query(None)
    vehicleStatus:Optional[str]=Query(None)
    slotId:Optional[int]=Query(None)

class ExtraFeatures(BaseModel):
    # bookingPassId:int
    count:int
    floorFeaturesId:int
    extraDetail:str

class UserSlot(BaseModel):
    slotId:int
    vehicleType:int

class ExtraFees(BaseModel):
    # bookingPassId:int
    priceId:int
    count:int
    extraFee:float
    extraFeesDetails:Optional[str]=Query(None)

class BookingMaster(BaseModel):
    parkingOwnerId: int
    branchId:int
    blockId:int
    floorId:int
    userId:Optional[int]=Query(None)
    phoneNumber:str
    booking:str
    loginType:str
    bookingDurationType:str
    fromTime:Optional[time]=Query(None)
    toTime:Optional[time]=Query(None)
    fromDate:Optional[date]=Query(None)
    toDate:Optional[date]=Query(None)
    Dates:Optional[str]=Query(None)
    accessories:str
    bookingType:str
    subscriptionId:Optional[int]=Query(None)
    taxId:int
    # taxAmount:float
    totalAmount:Optional[float]=Query(None)
    paidAmount:Optional[float]=Query(None)
    paymentStatus:str
    paymentType:Optional[int]=Query(None)
    offerId:Optional[int]=Query(None)
    transactionId:Optional[str]=Query(None)
    bankName:Optional[str]=Query(None)
    bankReferenceNumber:Optional[str]=Query(None)
    pinNo:str
    createdBy:int
    vehicleHeaderDetails:Optional[List[VehicleHeader]]=Query(None)
    extraFeaturesDetails:Optional[List[ExtraFeatures]]=Query(None)
    userSlotDetails:Optional[List[UserSlot]]=Query(None)
    extraFeesDetails:Optional[List[ExtraFees]]=Query(None)


class PassVehicleHeader(BaseModel):
    # bookingPassId:int
    # vehicleNumberType:Optional[int]=Query(None)
    vehicleType:int
    vehicleNumber:str
    inTime:Optional[datetime]=Query(None)
    outTime:Optional[datetime]=Query(None)
    vehicleStatus:Optional[str]=Query(None)

class PassExtraFeatures(BaseModel):
    # bookingPassId:int
    count:int
    floorFeaturesId:int
    extraDetail:str

class PassUserSlot(BaseModel):
    # bookingPassId:int
    slotId:int
    vehicleType:int

class PassExtraFees(BaseModel):
    # bookingPassId:int
    priceId:int
    count:int
    extraFee:float
    extraFeesDetails:Optional[str]=Query(None)

class PassBokking(BaseModel):
    passTransactionId:int
    blockId:int
    floorId:int
    totalAmount:Optional[str]=Query(None)
    paymentStatus:Optional[str]=Query(None)
    paymentType:int
    transactionId:Optional[str]=Query(None)
    bankName:Optional[str]=Query(None)
    bankReferenceNumber:Optional[str]=Query(None)
    createdBy:int
    vehicleHeaderDetails:List[PassVehicleHeader]
    extraFeaturesDetails:Optional[List[PassExtraFeatures]]=Query(None)
    userSlotDetails:Optional[List[PassUserSlot]]=Query(None)
    extraFeesDetails:Optional[List[PassExtraFees]]=Query(None)

class CancellationUpdate(BaseModel):
    bookingId:int
    refundStatus:str
    cancellationCharges:float
    cancellationReason:str
    updatedBy:int
