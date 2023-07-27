import json
from sqlalchemy import create_engine
from mail import sendEmail
from sms import sendSMS
from routers.fireBaseNotification import send_topic_push
import os
import requests

engine = create_engine("mssql+pyodbc://sqldeveloper:SqlDeveloper$@192.168.1.221/smart_parking_notification_service?driver=ODBC+Driver+17+for+SQL+Server")

def signupNotification(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='SignUp' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'): 
                    Data={"subject":i["subject"],"contact":message['emailId'],"mail_content":i["messageBody"]}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])

def gettingPassNotification(message):
    
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='After Getting Pass' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"].replace("[pass type]",message['passType']).replace("[parking name]",message['parkingName'])
                    Message_str = i["messageBody"].replace("[user name]",message['userName']).replace("[pass Type]",message['passType']).replace("[parking name]",message['parkingName']).replace("[fromDate]",message['fromDate']).replace("[toDate]",message['toDate']).replace("[link]",'prematix.com')
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])

def gettingOwnerCancellation(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Owner Cancellation' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"]
                    Message_str = i["messageBody"].replace("[customerName]",message['customerName']).replace("[parkingName]",message['parkingName']).replace("[reason]",message['cancellationReason'])
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])
def gettingOwnerApproval(message):
   
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Owner' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"].replace("[Name of parking]",message['parkingName'])
                    Message_str = i["messageBody"].replace("[customer name]",message['customerName'])
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])

def gettingBranchCancellation(message):
   
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Branch Cancellation' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"]
                    Message_str = i["messageBody"].replace("[customerName]",message['customerName']).replace("[Name of Branch]",message['branchName']).replace("[Name of parking]",message['parkingName']).replace("[reason]",message['cancellationReason'])
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])

def gettingBranchApproval(message):
   
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Branch' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"].replace("[Name of branch]",message['branchName']).replace("[Name of parking]",message['parkingName'])
                    Message_str = i["messageBody"].replace("[customer name]",message['customerName'])
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])

def gettingBlockCancellation(message):
   
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Block Cancellation' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"]
                    Message_str = i["messageBody"].replace("[customerName]",message['customerName']).replace("[Name of Block]",message['blockName']).replace("[Name of Branch]",message['branchName']).replace("[reason]",message['cancellationReason'])
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])
def gettingBlockApproval(message):
   
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Block' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"].replace("[Name of branch]",message['branchName']).replace("[Name of block]",message['blockName'])
                    Message_str = i["messageBody"].replace("[customer name]",message['customerName'])
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])

def passwordRecoveryNotification(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Password Recovery' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'): 
                    Message_str = i["messageBody"].replace("[customer name]",message['userName'])
                    Data={"subject":i["subject"],"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])

def OTPNotification(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='OTP' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'): 
                    Message_str = i["messageBody"].replace("[OTP Number]",str(message['OTP'])).replace("[customerName]",message['userName'])
                    Data={"subject":i["subject"],"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)
                if message.get('userId') !=0 and message.get('registrationToken'):
                    res=send_topic_push(message.get('registrationToken'),i["subject"], Message_str, message.get('userId'))
                    return res     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"].replace("[OTP]",str(message['OTP'])),i["peid"],i["tpid"])

def subscriptionNotification(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Subscription' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'): 
                    Message_str = i["messageBody"].replace("[customer name]",message['userName'])
                    Data={"subject":i["subject"],"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])

def offerCodeNotification(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Offer Code' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'): 
                    Message_str = i["messageBody"].replace("[name]",message['userName']).replace("[Parking name]",message['parkingName']).replace("[WELCOME]",message['offerCode'])
                    Data={"subject":i["subject"],"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])

def bookingNotification(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Booking' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"].replace("[Name of parking]",message['parkingName'])
                    Message_str = i["messageBody"].replace("[customer name]",message['userName']).replace("[link]",'http://prematix.tech/summaryPage')
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)
                if message.get('userId') !=0 and message.get('registrationToken'):
                    res=send_topic_push(message.get('registrationToken'),Subject_str, Message_str, message.get('userId'))
                    return res
                else:
                    if i["templateType"]=='S' and message.get('phoneNo'):
                        sendSMS("smart-parking",message['phoneNo'],i["messageBody"].replace("[link]",'http://prematix.tech/summaryPage'),i["peid"],i["tpid"])

def bookingDateTimeExtendNotification(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='payment and booking' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"].replace("[Vehicle type parking]",message['vehicleTypeName'])
                    Message_str = i["messageBody"].replace("[Name]",message['userName']).replace("[parking name]",message['parkingName']).replace("[Vehicle type parking]",message['vehicleTypeName'])
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])


def bookingPaidAmountNotification(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='payment and booking' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"].replace("[Vehicle type parking]",message['vehicleTypeName'])
                    Message_str = i["messageBody"].replace("[Name]",message['userName']).replace("[parking name]",message['parkingName']).replace("[Vehicle type parking]",message['vehicleTypeName'])
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])

def bookingPaymentstatusNotification(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='payment and booking' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"].replace("[Vehicle type parking]",message['vehicleTypeName'])
                    Message_str = i["messageBody"].replace("[Name]",message['userName']).replace("[parking name]",message['parkingName']).replace("[Vehicle type parking]",message['vehicleTypeName'])
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])


def vehicleHeaderIntimeNotification(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Checkin' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"].replace("[Name of parking]",message['parkingName'])
                    Message_str = i["messageBody"].replace("[customer name]",message['userName']).replace("[vehicle type parking]",message['vehicleTypeName']).replace("[date-time]",message['inTime'])
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)
                if message.get('userId') !=0 and message.get('registrationToken'):
                    res=send_topic_push(message.get('registrationToken'),Subject_str, Message_str, message.get('userId'))
                    return res     
                else:
                    if i["templateType"]=='S' and message.get('phoneNo'):
                        sendSMS("smart-parking",message['phoneNo'],i["messageBody"],i["peid"],i["tpid"])

def vehicleHeaderOuttimeNotification(message):
    with engine.connect() as cur:
        result=cur.execute(f"""SELECT CAST((SELECT * FROM messageTemplatesView WHERE messageHeader='Checkout' ORDER BY templateType FOR JSON PATH) AS VARCHAR(MAX))""")
        row = result.fetchone()
        if row[0] != None:
            for i in json.loads(row[0]):
                if i["templateType"]=='M' and message.get('emailId'):
                    Subject_str=i["subject"].replace("[Name of parking]",message['parkingName'])
                    Message_str = i["messageBody"].replace("[customer name]",message['userName']).replace("[vehicle type parking]",message['vehicleTypeName']).replace("[date-time]",message['outTime'])
                    Data={"subject":Subject_str,"contact":message['emailId'],"mail_content":Message_str}
                    sendEmail(Data)
                if message.get('userId') !=0 and message.get('registrationToken'):
                    res=send_topic_push(message.get('registrationToken'),Subject_str, Message_str, message.get('userId'))
                    return res     
                elif i["templateType"]=='S' and message.get('phoneNo'):
                    sendSMS("smart-parking",message['phoneNo'],i["messageBody"].replace("customer name",message['userName']).replace("vehicle type parking",message['vehicleName']).replace("date-time",message['outTime']),i["peid"],i["tpid"])




callbackDic = {'signUp':signupNotification,
                'After Getting Pass':gettingPassNotification,
                'Owner Cancellation':gettingOwnerCancellation,
                'Owner':gettingOwnerApproval,
                'Branch Cancellation':gettingBranchCancellation,
                'Branch':gettingBranchApproval,
                'Block Cancellation':gettingBlockCancellation,
                'Block':gettingBlockApproval,
                'Password Recovery':passwordRecoveryNotification,
                'OTP':OTPNotification,
                'Subscription':subscriptionNotification,
                'Offer Code':offerCodeNotification,
                'booking':bookingNotification,
                'bookingDateTimeExtendmail':bookingDateTimeExtendNotification,
                'bookingpaidAmountmail':bookingPaidAmountNotification,
                'paymentstatusmail':bookingPaymentstatusNotification,
                'vehicleIntimemail':vehicleHeaderIntimeNotification,
                'vehicleOuttimemail':vehicleHeaderOuttimeNotification
                }



def callback(message):
    
    message = json.loads(message)
    print("message",message)
    callbackDic[message['action']](message['body'])
