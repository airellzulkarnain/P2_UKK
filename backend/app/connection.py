import mysql.connector
import json


config = dict()
with open('app/config.json', 'r') as file: 
   config = json.loads(file.read())
db = mysql.connector.connect(**config['database'])
cursor = db.cursor(dictionary=True)
