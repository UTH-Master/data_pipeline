# Config MongoDB
MONGODB_URI = "mongodb://km2401:km2401@tuanhoangdinh.ddns.net:27017/example_db"
DATABASE_NAME = "example_db"
COLLECTION_NAME = "images"

# Camera ID
CAMERA_IDS = [
    "65e0552f6b18080018db6647",
    "5d8cdc57766c88001718896e",
    "63b66035bfd3d90017eaa48e",
]
CAPTURE_INTERVAL = 5  # seconds

IMAGE_URL_BASE = "http://giaothong.hochiminhcity.gov.vn/render/ImageHandler.ashx"

# Config logger
LOG_FILE = "camera_system_error.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"