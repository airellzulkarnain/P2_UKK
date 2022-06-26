import mysql.connector
import json


class MySQLConnection:
   config = dict()
   with open('app/config.json', 'r') as file: 
      config = json.loads(file.read())

   def __init__(self):
      self.db = mysql.connector.connect(**self.config['database'])
      self.cursor = self.db.cursor(dictionary=True)

   def execute(self, command: str, value: tuple | dict | list | None = None):
      if command and value:
         self.cursor.execute(command, value)
      elif command:
         self.cursor.execute(command)

   def open(self):
      self.db = mysql.connector.connect(**self.config['database'])
      self.cursor = self.db.cursor(dictionary=True)

   def close(self):
      self.cursor.close()
      self.db.close()

   def fetchone(self):
      return self.cursor.fetchone()

   def fetchall(self):
      return self.cursor.fetchall()

   def commit(self):
      self.db.commit()

   def lastrowid(self):
      return self.cursor.lastrowid
