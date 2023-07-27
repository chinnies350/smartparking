import json
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from task import postFloorName
from routers.config import redis_client

engine = create_engine("mssql+pyodbc://sqldeveloper:SqlDeveloper$@192.168.1.221/smart_parking_slot_service?driver=ODBC+Driver+17+for+SQL+Server")
# # import pyodbc

# connection = pyodbc.connect(
#         r'Driver={SQL Server};'
#         # r'Driver={SQL Server};' 
#         r'Server=192.168.1.221;'
#         r'Database=smart_slot;'
#         r'UID=sqldeveloper;'
#         r'PWD=SqlDeveloper$;'
#         r'MARS_Connection=yes;'
#         r'APP=yourapp')

# cur = connection.cursor()

dic = {}

# callback action functions
def slotblock(slotId):
    with engine.connect() as conn:
        # print(slotId)
        if slotId['inOut']=='I':
            conn.execute(f"""UPDATE parkingSlot SET slotState = 'B'  where parkingSlotId = ?""", slotId['slotId'])
        else:
            conn.execute(f"""UPDATE parkingSlot SET slotState = 'N'  where parkingSlotId = ?""", slotId['slotId'])


def bookingdatetimeextend(slotId):
    with engine.connect() as conn:
        conn.execute(f"""UPDATE parkingSlot SET slotState = 'N'  where parkingSlotId = ?""", slotId['slotId'])


def passbookingactivestatus(slotId):
    # print('slotId',slotId)
    with engine.connect() as conn:
        conn.execute(f"""UPDATE parkingSlot SET slotState = 'B'  where parkingSlotId = ?""", slotId['slotId'])


def postbookingblock(slotId):
    # print('slotId',slotId)
    with engine.connect() as conn:
        conn.execute(f"""UPDATE parkingSlot SET slotState = 'B'  where parkingSlotId = ?""", slotId['slotId'])
    

def insertUser(message):
    pass

def blockSlot(message):
    pass


def postFloorMaster(request):
    print("postFloorMaster called")
    floorName = redis_client.hget('configMaster', request['floorName'])
    parkingName = redis_client.hget('parkingOwnerMaster', request['parkingOwnerId'])
    branchName = redis_client.hget('branchMaster', request['branchId'])
    blockName = redis_client.hget('blockMaster', request['blockId'])
    floorTypeName = redis_client.hget('configMaster', request['floorType'])
    
    floorName=floorName.decode("utf-8")  if floorName else None
    parkingName=parkingName.decode("utf-8") if parkingName else None
    branchName=branchName.decode("utf-8")  if branchName else None
    blockName=blockName.decode("utf-8") if blockName else None
    floorTypeName=floorTypeName.decode("utf-8")  if floorTypeName else None
    with engine.connect() as conn:
        result=conn.execute(f"""
                        INSERT INTO floorMaster(parkingOwnerId,parkingName,branchId,branchName,blockId,blockName,floorName,floorConfigName,floorType,floorTypeName,squareFeet,activeStatus,createdBy,createdDate)
                        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,GETDATE())
                      """, (request['parkingOwnerId'],
                            parkingName,
                            request['branchId'],
                            branchName,
                            request['blockId'],
                            blockName,
                            request['floorName'],
                            floorName,
                            request['floorType'],
                            floorTypeName,
                            request['squareFeet'],
                            request['activeStatus'],
                            request['createdBy']
                            ))
        result.close()
        if result.rowcount>=1:
            res=conn.execute(f"""SELECT TOP 1 floorId FROM floorMaster where parkingOwnerId=? and branchId=?
								and blockId=? and floorType=? ORDER BY floorId DESC """,(request['parkingOwnerId'],request['branchId'],request['blockId'],request['floorType']))
            row = res.fetchone()
            res.close()
            if row[0]!=None:
                postFloorName.delay(int(row[0]),floorName)

callbackDic = {
    'block': slotblock,
    'datetimeextend': bookingdatetimeextend,
    'passbooking': passbookingactivestatus,
    'postbooking': postbookingblock,
    'blockSlot': blockSlot,
    'insertuser': insertUser,
    'postFloorMaster': postFloorMaster
}


# function dictionary
# dic["blockSlot"] = blockSlot


# def callback(body):
#     body = json.loads(body)
#     print(f"body {body} body type {type(body)}")
#     callbackDic[body["action"]](body["message"])
#     print(" [x] Received %r" % body)


def callback(message):
    # pass    
    # print ('message',message,type(message))
    message = json.loads(message)
    callbackDic[message['action']](message['body'])