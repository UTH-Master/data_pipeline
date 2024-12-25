import pandas as pd
import os
import logging

# Config minIO
MINIO_ENDPOINT = "play.min.io:9000"
MINIO_ACCESS_KEY = "FSzyH6P8UqAzPg4YFxhP"
MINIO_SECRET_KEY = "iReyzp0S7gGael8wJmDEG8up26MMpol82f3QDGJi"
MINIO_SECURE = True
BUCKET_NAME = "camera-images-json"

# Get camera IDs from CSV file
df = pd.read_csv('../Thong_tin_nguon_camera.csv')
CAMERA_IDS = df['ID'].tolist()

CAPTURE_INTERVAL = 5  # seconds

IMAGE_URL_BASE = "http://giaothong.hochiminhcity.gov.vn/render/ImageHandler.ashx"

# Config logger
LOG_FILE = "camera_system_error.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)) 

urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.WARNING)
urllib3_logger.addHandler(file_handler) 