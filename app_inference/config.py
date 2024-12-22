import os

URL = "https://www.youtube.com/watch?v=cB9Fs9UmcRU"
OPTIONS = {
    "STREAM_RESOLUTION": '720p', 
    "STREAM_PARAMS": {"nocheckcertificate": True}
}
LINE_POSITION = (300, 450, 900, 450) 

LIST_VEHICLE = ["car", "motorcycle", "bicycle",  "bus", "truck"]

SIGNAL_STOP = False

DB_CONFIG = {
    'dbname': 'traffic_db',
    'user': 'postgres',
    'password': 'adminadmin123',
    'host': '42.119.182.248', 
    'port': '5432',      
}