import base64
import json
import datetime
from io import BytesIO
import cv2

def encode_image_to_base64(frame):
    _, buffer = cv2.imencode('.jpg', frame)
    return base64.b64encode(buffer).decode('utf-8')

