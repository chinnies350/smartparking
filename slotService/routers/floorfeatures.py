from fastapi import Query
from fastapi.routing import APIRouter
from typing import Optional,List
from routers.config import get_cursor
from fastapi import Depends
from aioodbc.cursor import Cursor
import json,os
import routers
import schemas
import asyncio
import ast
from dotenv import load_dotenv
load_dotenv()

router = APIRouter(prefix='/floorfeatures',tags=['floorfeatures'])

        


    


#######################***********************************************************************#################################

async def floorfeaturesDetailsBasedOnfeaturesId(featuresId,branchId,floorId,parkingOwnerId,taxId,activeStatus,featuresIds,db):

    try:        
        await db.execute(f"""SELECT CAST((select ff.*,fm.blockId,fm.blockName from floorFeatures as ff
                            inner join floorMaster as fm on fm.floorId=ff.floorId where ff.featuresId=?
                            FOR JSON PATH) AS VARCHAR(MAX))""",(featuresId))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def floorfeaturesDetailsBasedOnbranchId(featuresId,branchId,floorId,parkingOwnerId,taxId,activeStatus,featuresIds,db):
    try:        
        await db.execute(f"""SELECT CAST((select ff.*,fm.blockId,fm.blockName from floorFeatures as ff
inner join floorMaster as fm on fm.floorId=ff.floorId where ff.branchId=?
                    FOR JSON PATH) AS VARCHAR(MAX))""",(branchId))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def floorfeaturesDetailsBasedOnfloorId(featuresId,branchId,floorId,parkingOwnerId,taxId,activeStatus,featuresIds,db):
    try:        
        await db.execute(f"""SELECT CAST((select ff.*,fm.blockId,fm.blockName from floorFeatures as ff
inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=?
                    FOR JSON PATH) AS VARCHAR(MAX))""",(floorId))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def floorfeaturesDetailsBasedOnparkingOwnerId(featuresId,branchId,floorId,parkingOwnerId,taxId,activeStatus,featuresIds,db):
    try:        
        await db.execute(f"""SELECT CAST((select ff.*,fm.blockId,fm.blockName from floorFeatures as ff
inner join floorMaster as fm on fm.floorId=ff.floorId where ff.parkingOwnerId=?
                    FOR JSON PATH) AS VARCHAR(MAX))""",(parkingOwnerId))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def floorfeaturesDetailsBasedOnTaxId(featuresId,branchId,floorId,parkingOwnerId,taxId,activeStatus,featuresIds,db):
    try:        
        await db.execute(f"""SELECT CAST((select ff.*,fm.blockId,fm.blockName from floorFeatures as ff
inner join floorMaster as fm on fm.floorId=ff.floorId where ff.taxId=?
                    FOR JSON PATH) AS VARCHAR(MAX))""",(taxId))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def floorfeaturesDetails(featuresId,branchId,floorId,parkingOwnerId,taxId,activeStatus,featuresIds,db):
    try:        
        await db.execute(f"""SELECT CAST((select ff.*,fm.blockId,fm.blockName from floorFeatures as ff
inner join floorMaster as fm on fm.floorId=ff.floorId 
                    FOR JSON PATH) AS VARCHAR(MAX))""")
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

        
        
async def floorfeaturesDetailsBasedOnActiveStatus(featuresId,branchId,floorId,parkingOwnerId,taxId,activeStatus,featuresIds,db):
    try:        
        await db.execute(f"""SELECT CAST((select ff.*,fm.blockId,fm.blockName from floorFeatures as ff
inner join floorMaster as fm on fm.floorId=ff.floorId where ff.activeStatus=?
                    FOR JSON PATH) AS VARCHAR(MAX))""",(activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
    
async def floorfeaturesDetailsBasedOnfloorIdAndActiveStatus(featuresId,branchId,floorId,parkingOwnerId,taxId,activeStatus,featuresIds,db):
    try:        
        await db.execute(f"""SELECT CAST((select ff.*,fm.blockId,fm.blockName from floorFeatures as ff
inner join floorMaster as fm on fm.floorId=ff.floorId where ff.floorId=? and ff.activeStatus=?
                    FOR JSON PATH) AS VARCHAR(MAX))""",(floorId,activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }
        
        
async def floorfeaturesDetailsBasedOnfeaturesIdAndActiveStatus(featuresId,branchId,floorId,parkingOwnerId,taxId,activeStatus,featuresIds,db):
    try:        
        await db.execute(f"""SELECT CAST((select ff.*,fm.blockId,fm.blockName from floorFeatures as ff
inner join floorMaster as fm on fm.floorId=ff.floorId where ff.featuresId=? and ff.activeStatus=?
                    FOR JSON PATH) AS VARCHAR(MAX))""",(featuresId,activeStatus))
        row = await db.fetchone()
        if row[0] != None:
            data=(json.loads(row[0]))                
            return {
                "response":data,
                "statusCode":1
                }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as allDetails ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }

async def floorFeaturesDetailsBasedOnFeaturesIds(featuresId,branchId,floorId,parkingOwnerId,taxId,activeStatus,featuresIds,db):
    try:
        
       
        for i in ast.literal_eval(featuresIds[0]):
              
            await db.execute(f"""SELECT CAST((SELECT ISNULL(SUM(ff.totalAmount *{i['count']}),0) AS extraFeaturesTotalAmount,ISNULL(SUM(ff.Amount *{i['count']}),0) AS extraFeaturesAmount,ISNULL(SUM(ff.tax *{i['count']}),0) AS extraFeaturesTaxAmount
                                                FROM floorFeatures as ff
                                                WHERE ff.featuresId IN {tuple(i['floorFeaturesId'] for i in ast.literal_eval(featuresIds[0]))+tuple('0')}
                                            FOR JSON PATH) AS VARCHAR(MAX))
                        """)
        row = await db.fetchone()
        
        if row[0] != None:  
            return {
                "response":json.loads(row[0]),
                "statusCode":1
                }
        else:
            return {
                "response":"Data Not Found",
                "statusCode":0
            }
    except Exception as e:
        print("Exception as floorFeaturesDetailsBasedOnFeaturesIds ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }


floorfeatureDict = {
    "featuresId=True, branchId=False, floorId=False, parkingOwnerId=False, taxId=False,activeStatus=False, featuresIds=False":floorfeaturesDetailsBasedOnfeaturesId,
    "featuresId=False, branchId=True, floorId=False, parkingOwnerId=False, taxId=False,activeStatus=False, featuresIds=False":floorfeaturesDetailsBasedOnbranchId,
    "featuresId=False, branchId=False, floorId=True, parkingOwnerId=False, taxId=False,activeStatus=False, featuresIds=False":floorfeaturesDetailsBasedOnfloorId,
    "featuresId=False, branchId=False, floorId=False, parkingOwnerId=True, taxId=False,activeStatus=False, featuresIds=False":floorfeaturesDetailsBasedOnparkingOwnerId,
    "featuresId=False, branchId=False, floorId=False, parkingOwnerId=False, taxId=True,activeStatus=False, featuresIds=False":floorfeaturesDetailsBasedOnTaxId,
    "featuresId=False, branchId=False, floorId=False, parkingOwnerId=False, taxId=False,activeStatus=True, featuresIds=False":floorfeaturesDetailsBasedOnActiveStatus,
    "featuresId=False, branchId=False, floorId=True, parkingOwnerId=False, taxId=False,activeStatus=True, featuresIds=False":floorfeaturesDetailsBasedOnfloorIdAndActiveStatus,
    "featuresId=True, branchId=False, floorId=False, parkingOwnerId=False, taxId=False,activeStatus=True, featuresIds=False":floorfeaturesDetailsBasedOnfeaturesIdAndActiveStatus,
    "featuresId=False, branchId=False, floorId=False, parkingOwnerId=False, taxId=False,activeStatus=False, featuresIds=True":floorFeaturesDetailsBasedOnFeaturesIds,
    "featuresId=False, branchId=False, floorId=False, parkingOwnerId=False, taxId=False,activeStatus=False, featuresIds=False":floorfeaturesDetails
}

##################################################################################################################
@router.get('')
async def floorfeatureGet(featuresId:Optional[int]=Query(None),branchId:Optional[int]=Query(None),floorId:Optional[int]=Query(None),parkingOwnerId:Optional[int]=Query(None) , taxId:Optional[int]=Query(None),activeStatus:Optional[int]=Query(None), featuresIds:Optional[List]=Query(None), db:Cursor = Depends(get_cursor)):
    try:
        st = f"featuresId={True if featuresId else False}, branchId={True if branchId else False}, floorId={True if floorId else False}, parkingOwnerId={True if parkingOwnerId else False}, taxId={True if taxId else False},activeStatus={True if activeStatus else False}, featuresIds={True if featuresIds else False}"
        return await floorfeatureDict[st](featuresId,branchId,floorId,parkingOwnerId,taxId,activeStatus,featuresIds,db)
    except Exception as e:
        print("Exception as floorfeatureGet ",str(e))
        return {
            "response":"Server Error",
            "statusCode":0
        }



@router.post('')
async def postfloorFeatures(request:schemas.PostfloorFeatures,db:Cursor=Depends(get_cursor)):
    try:
        url = f"{os.getenv('ADMIN_SERVICE_URL')}/taxMaster?taxId={request.taxId}"
        response = await routers.client.get(url)   
        var=json.loads(response.text)
        if var['statusCode'] !=0:
            tax=request.totalAmount * (var['response'][0]['taxPercentage']) / 100
            await db.execute(f"""
                        EXEC [dbo].[postfloorFeatures] 
                        @parkingOwnerId=?,
                        @branchId=?,
                        @floorId=?,
                        @featureName=?,
                        @description=?,
                        @taxId=?,
                        @totalAmount=?,
                        @createdBy=?,
                        @tax=?
                      """,
                      (request.parkingOwnerId,
                        request.branchId,
                        request.floorId,
                        request.featureName,
                        request.description,
                        request.taxId,
                        request.totalAmount,
                        request.createdBy,
                        tax
                      ))
            row=await db.fetchone()
            await db.commit()
            return{"statusCode":int(row[1]),"response":row[0]}
            
        else:
            return{"statusCode": 0,"response":'Tax not found'} 
    except Exception as e:
        print("Exception as postfloorFeatures ",str(e))
        return{
        "statusCode": 0,
        "response":"Server Error"   
        } 

@router.put('')
async def putFloorFeatures(request:schemas.PutfloorFeaures,db:Cursor=Depends(get_cursor)):
    try:
        url = f"{os.getenv('ADMIN_SERVICE_URL')}/taxMaster?taxId={request.taxId}"
        response = await routers.client.get(url)   
        var=json.loads(response.text)
        if var['statusCode'] !=0:
            tax=request.totalAmount * (var['response'][0]['taxPercentage']) / 100
            url = f"{os.getenv('BOOKING_URL')}/extraFeatures?floorFeaturesId={request.featuresId}"
            response = await routers.client.get(url)   
            extraFeaturesRes=json.loads(response.text)
            if extraFeaturesRes.get('statusCode')==1 and len(extraFeaturesRes.get('response'))!=0:
                extraFeaturesRes=extraFeaturesRes['response'][0]['extraFeatureId']
            else:
                extraFeaturesRes=None
            await db.execute(f"""
                               EXEC [dbo].[putfloorFeatures] 
                               @featuresId=?,
                               @featureName=?,
                               @description=?,
                               @taxId=?,
                               @tax=?,
                               @taxName=?,
                               @serviceName=?,
                               @taxPercentage=?,
                               @totalAmount=?,
                               @floorId=?,
                               @updatedBy=?,
                               @extraFeaturesRes=?
                               """,
                                (
                                 request.featuresId,
                                 request.featureName,
                                 request.description,
                                 request.taxId,
                                 tax,
                                 var['response'][0]['taxName'],
                                 var['response'][0]['serviceName'],
                                 var['response'][0]['taxPercentage'],
                                 request.totalAmount,
                                 request.floorId,
                                 request.updatedBy,
                                 extraFeaturesRes
                                ))
            row=await db.fetchone()
            await db.commit()
            return{"statusCode":int(row[1]),"response":row[0]}
            
        else:
            return{"statusCode": 0,"response":'Tax not found'} 
    except Exception as e:
        print("Exception as postfloorFeatures ",str(e))
        return{
        "statusCode": 0,
        "response":"Server Error"   
        }


@router.delete('')
async def deleteFloorFeatures(featuresId:int,activeStatus:str,db:Cursor = Depends(get_cursor)):
    try:
        result=await db.execute("UPDATE floorFeatures SET activeStatus=? WHERE featuresId=?",activeStatus,featuresId)
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
        print("Exception as deleteFloorFeatures ",str(e))
        return{"stausCode":0, "response":"Server Error"}
