from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib

def sendEmail(Data):
    print("jjj",Data["subject"])
    sender_address = 'prematixdev@gmail.com'
    sender_pass = 'yunvuhkngyjzirob'
    receiver_address = Data["contact"]
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = Data["subject"]
    message.attach(MIMEText(Data["mail_content"], 'plain'))
    session = smtplib.SMTP('smtp.gmail.com',587)
    session.starttls()
    session.login(sender_address, sender_pass)
    text = message.as_string()
    session.sendmail(sender_address, receiver_address, text)
    session.quit()

    return {"statusCode": 1, "response": "E-Mail Sent Sucessfully!"}