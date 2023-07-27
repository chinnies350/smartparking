# import firebase_admin
# from firebase_admin import credentials, messaging
# from pymongo.mongo_client import MongoClient
# from fastapi.routing import APIRouter
# from aioodbc.cursor import Cursor
# from fastapi import Depends
# from routers.config import get_cursor
# import schemas

# cred = credentials.Certificate('routers/services/paypre-parking-firebase.json')
# admin = firebase_admin.initialize_app(cred)


# client = MongoClient("mongodb://admin:Prematix%40123@192.168.1.169:7017/?authMechanism=DEFAULT")
# db = client['fireBase_notification']
# col = db['fireBase_notification']

# # registration_token = ['token']

# router=APIRouter(prefix="/fireBaseNotification",tags=['fireBaseNotification'])

# @router.post('')
# async def postFireBaseNotification(request:schemas.FireBaseNotification, db: Cursor = Depends(get_cursor)):
#     try:
#         await db.execute(f"""SELECT registrationToken FROM userMaster WHERE userId = ?""", (request.userId))
#         row = await db.fetchone()
#         if row[0]:
#             res=send_topic_push(row[0],request.title, request.body, request.userId)
#             return res
#         else:
#             return {
#                 "response":'Please Add Registration Token',
#                 "statusCode":0
#             }
#     except Exception as e:
#         print("Exception as postFireBaseNotification",str(e))
#         return {'statusCode':0,'response':"Server Error"}

# def send_topic_push(token, title, body, userId):
#     try:
#         message = messaging.Message(
#             notification=messaging.Notification(
#             title=title,
#             body=body
#             ),
#             token=token
#         )
#         response = messaging.send(message)
#         col.insert_one({
#             'userId': userId,
#             'title': title,
#             'message': body,
#             'messageId': response
#         })
#         return {'statusCode':1,'response':'Data Sent Successfully'}
#     except Exception as e:
#         print("Exception as send_topic_push",str(e))
#         return {'statusCode':0,'response':"Server Error"}



# def getMessageByUserId(userId):
#     data = []
#     res = col.find({"userId": userId}, {'_id':0})
#     for i in res:
#         data.append(i)
#     return {
#         'statusCode':1,
#         'response':data
#     }
