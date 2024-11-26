import pandas as pd
import os

# Config MongoDB
MONGODB_URI = "mongodb://km2401:km2401@tuanhoangdinh.ddns.net:27017/example_db"
DATABASE_NAME = "example_db"
COLLECTION_NAME = "images"

# Get camera IDs from CSV file
df = pd.read_csv('../Thong_tin_nguon_camera.csv')
CAMERA_IDS = df['ID'].tolist()

CAPTURE_INTERVAL = 5  # seconds

IMAGE_URL_BASE = "http://giaothong.hochiminhcity.gov.vn/render/ImageHandler.ashx"

# Config logger
LOG_FILE = "camera_system_error.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"