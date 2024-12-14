# Chu Duy Anh - 2480101001
# File cấu hình cho hệ thống lưu trữ ảnh và luồng livestream sử dụng MongoDB

import pandas as pd
import os

# MongoDB Configuration
MONGODB_URI = "mongodb://km2401:km2401@tuanhoangdinh.ddns.net:27017/example_db"
DATABASE_NAME = "example_db"
COLLECTION_IMAGE_NAME = "images"
COLLECTION_STREAM_NAME = "streams"

# Get camera IDs from CSV file
df = pd.read_csv('../Thong_tin_nguon_camera.csv')
CAMERA_IDS = df['ID'].tolist()

CAPTURE_INTERVAL = 5  # seconds

IMAGE_URL_BASE = "http://giaothong.hochiminhcity.gov.vn/render/ImageHandler.ashx"

# YouTube Stream Configuration
YOUTUBE_STREAMS = {
    "stream1": "https://www.youtube.com/watch?v=b6fkug3AmH4",
    "stream2": "https://www.youtube.com/watch?v=cB9Fs9UmcRU",
    "stream3": "https://www.youtube.com/watch?v=Fu3nDsqC1J0",
    "stream4": "https://www.youtube.com/watch?v=IXBTD4VgFF4",
    "stream5": "https://www.youtube.com/watch?v=F06HWCf22-Q"
}

CAPTURE_STREAM_INTERVAL = 0.1  # seconds

# Config logger
LOG_FILE = "camera_system_error.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
