from  sqlalchemy import create_engine
import json

engine = create_engine("mssql+pyodbc://sqldeveloper:SqlDeveloper$@192.168.1.221/smart_slots?driver=ODBC+Driver+17+for+SQL+Server")


functionMap = {}

def callback(message):
    message = json.loads(message)
    functionMap[message["action"]](message['body'])