import os

URL = "https://www.youtube.com/watch?v=cB9Fs9UmcRU"
OPTIONS = {
    "STREAM_RESOLUTION": '720p', 
    "STREAM_PARAMS": {"nocheckcertificate": True}
}
LINE_POSITION = (300, 450, 900, 450) 

VEHICLE_COUNTS = {
    "car": 0,
    "motorcycle": 0,
    "bicycle": 0,
    "bus": 0,
    "truck": 0

}

LIST_VEHICLE = ["car", "motorcycle", "bicycle",  "bus", "truck"]