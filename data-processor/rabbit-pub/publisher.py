""" Write Code Here """

#!/usr/bin/env python
import pika
import sys
import os

#-----------------------
sys.path.append(os.path.abspath(os.path.join('.')))
from db.utils import DatabaseConnector


db = DatabaseConnector(host="localhost",
                       database="mydb",
                       user="myuser",
                       password="mypassword",
                       port=5432)
db.connect()
last_row = db.get_last_row()
b_last_row = bytearray(str(last_row), 'utf-8')

db.close()

#-----------------------
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost',
                              virtual_host='myrabbitvhost',
                              credentials=pika.PlainCredentials('user', 'password')
                              )
)
channel = connection.channel()

channel.exchange_declare(exchange='logs', exchange_type='fanout')



channel.basic_publish(exchange='logs', routing_key='', body=b_last_row)
print(f" [x] Sent {b_last_row}")
connection.close()