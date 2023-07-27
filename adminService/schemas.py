from pydantic import BaseModel
from typing import Optional
from fastapi import Query
from datetime import datetime,date,time

class VehicleConfigMaster(BaseModel):
    vehicleName:str
    vehicleImageUrl:str
    vehiclePlaceHolderImageUrl: str
    vehicleKeyName:Optional[str]=Query(None)
    activeStatus:str
    createdBy:int

class PutVehicleConfigMaster(BaseModel):
    vehicleConfigId:int
    vehicleName:str
    vehicleImageUrl:str
    vehiclePlaceHolderImageUrl: str
    vehicleKeyName:str
    updatedBy:int

class TaxMaster(BaseModel):
    serviceName:int
    taxName:str
    taxDescription:Optional[str]
    taxPercentage:Optional[float]
    activeStatus:str
    effectiveFrom:date
    effectiveTill:date
    createdBy : int
    
class PutTaxMaster(BaseModel):
    serviceName:int
    taxId:int
    taxName:str
    taxDescription:Optional[str]
    taxPercentage:Optional[float]
    activeStatus:str
    effectiveFrom:date
    updatedBy : Optional[int]

class MenuOptions(BaseModel):
    parkingOwnerId:Optional[int]
    moduleId:int
    optionName:str
    activeStatus:str
    createdBy:int

class PutMenuOptions(BaseModel):
    parkingOwnerId:int
    moduleId:int
    optionId:int
    optionName:str
    activeStatus:str
    updatedBy:Optional[int]

class ConfigMaster(BaseModel):
    # parkingOwnerId :Optional[int]=Query(None)
    configTypeId : int
    configName : str
    activeStatus : str
    createdBy : int
    
class PutConfigMaster(BaseModel):
    # parkingOwnerId :Optional[int]=Query(None)
    configTypeId : int
    configId : int
    configName : str
    activeStatus : str
    updatedBy : Optional[int]

class ConfigType(BaseModel):
    typeName : str
    activeStatus : str
    createdBy : int
    
class PutConfigType(BaseModel):
    configTypeId : int
    typeName : str
    activeStatus : str
    updatedBy : Optional[int]

class Faq(BaseModel):
    offerId:Optional[int]=Query(None)
    question:str
    answer:str
    questionType:str
    activeStatus:str
    createdBy:int

class PutFaq(BaseModel):
    faqId:int
    offerId:Optional[int]=Query(None)
    question:str
    answer:str
    questionType:str
    updatedBy:int

class AppSettings(BaseModel):
    privacyPolicy:str
    termsAndConditions:str
    appVersion:int
    appType:str
    activeStatus:str
    createdBy:int

class PutAppSettings(BaseModel):
    privacyPolicy:str
    termsAndConditions:str
    appVersion:int
    appType:str
    updatedBy:int
    uniqueId:int

class ChargePinConfig(BaseModel):
    chargePinConfig:str
    chargePinImageUrl:str
    activeStatus:str
    createdBy:int

class PutChargePinConfig(BaseModel):
    chargePinId:int
    chargePinConfig:str
    chargePinImageUrl:str
    updatedBy:int

class PostParkingOwnerConfig(BaseModel):
    parkingOwnerId:int
    branchId:int
    blockOption:str
    floorOption:str
    squareFeet:Optional[int]=Query(None)
    floorType:Optional[int]=Query(None)
    employeeOption:str
    slotsOption:str
    createdBy:int


class PutParkingOwnerConfig(BaseModel):
    parkingOwnerConfigId:int
    parkingOwnerId:int
    branchId:int
    blockOption:str
    floorOption:str
    squareFeet:int
    floorType:int
    employeeOption:str
    slotsOption:str
    updatedBy:int