from pydantic import BaseModel
from typing import Dict, Optional,List
from fastapi import Query
from datetime import datetime,date,time
from xmlrpc.client import boolean


class FloorVehicleMasterDetails(BaseModel):
    vehicleType:int
    capacity:int
    length:str
    height:str
    rules:str
    activeStatus:str
    
class FloorFeaturesDetails(BaseModel):
    parkingOwnerId:int
    branchId:int
    featureName:str
    description:str
    amount:float
    taxId:int
    tax:float
    totalAmount:float
    
class FloorMaster(BaseModel):
    parkingOwnerId:int
    branchId:int
    blockId:int
    floorName:int
    floorType:int
    squareFeet:int
    activeStatus:str
    createdBy: int
    floorVehicleMasterDetails:Optional[List[FloorVehicleMasterDetails]] = None
    floorFeaturesDetails:Optional[List[FloorFeaturesDetails]] = None
    
class PutFloorMaster(BaseModel):
    floorId:int
    floorName:int
    floorType:int
    squareFeet:int
    activeStatus:str
    updatedBy: int

class PostfloorVehicleMaster(BaseModel):
    floorId:int
    vehicleType:int
    capacity:int
    length:str
    height:str
    rules:str
    activeStatus:str
    createdBy:int
    
class PutfloorVehicleMaster(BaseModel):
    floorId:int
    updatedBy:int
    floorVehicleId:int
    vehicleType:int
    capacity:int
    length:str
    height:str
    rules:str

class PostfloorFeatures(BaseModel):
    parkingOwnerId:int
    branchId:int
    floorId:Optional[int]=Query(None)
    featureName:str
    description:str
    taxId:int
    totalAmount:float
    activeStatus:str
    createdBy:int

class PutfloorFeaures(BaseModel):
    featuresId:int
    featureName:str
    description:str
    taxId:int
    totalAmount:float
    floorId:int
    updatedBy:int


class TimeSlabRules(BaseModel):
    priceId:int
    fromDate:datetime
    toDate:datetime
    activeStatus:str
    createdBy:int

class PriceMaster(BaseModel):
    parkingOwnerId:int
    branchId:int
    floorId:int
    totalAmount:float
    idType:str
    vehicle_accessories:int
    timeType:str
    taxId:int
    userMode:str
    activeStatus:str
    remarks:Optional[str]=Query(None)
    graceTime:Optional[int]=Query(None)
    createdBy:int
    
class PutPriceMaster(BaseModel):
    totalAmount:float
    idType:str
    taxId:int
    userMode:str
    graceTime:Optional[int]=Query(None)
    updatedBy:int
    priceId:int
    
class ParkingSlotDetails(BaseModel):
    laneNumber:Optional[str]=Query(None)
    slotNumber:str
    rowId:str
    columnId:str
    isChargeUnitAvailable:boolean
    chargePinType:int
    activeStatus:int
    createdBy:int

    
class parkingSlot(BaseModel):
    branchId:int
    blockId:int
    floorId:int
    parkingOwnerId:int
    typeOfVehicle:int
    noOfRows:int
    noOfColumns:int
    passageLeftAvailable:Optional[boolean]=Query(None)
    passageRightAvailable:Optional[boolean]=Query(None)
    typeOfParking:int
    activeStatus:str
    createdBy:int
    ParkingSlotDetails:List[ParkingSlotDetails]

class putparkingSlotDetails(BaseModel):
    laneNumber:str
    parkingSlotId :int
    parkingLotLineId:int
    slotNumber:str
    rowId:str
    columnId:str
    isChargeUnitAvailable:boolean
    chargePinType:int
    activeStatus:int
    updatedBy:int
    
class putparkingSlot(BaseModel):
    parkingLotLineId:int
    branchId:int
    blockId:int
    floorId:int
    parkingOwnerId:int
    typeOfVehicle:int
    noOfRows:int
    noOfColumns:int
    passageLeftAvailable:Optional[boolean]=Query(None)
    passageRightAvailable:Optional[boolean]=Query(None)
    typeOfParking:int
    activeStatus:str
    updatedBy:int
    ParkingSlotDetailsupdate:List[putparkingSlotDetails]

