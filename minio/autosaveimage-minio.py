import base64
import json
from minio import Minio
from minio.error import S3Error
import requests
from PIL import Image
import io
import threading
import time
from datetime import datetime
import logging
from config-minio import *

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

urllib3_logger = logging.getLogger('urllib3')
urllib3_logger.setLevel(logging.WARNING)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

# Config logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def init_minio():
    try:
        minio_client = Minio(
            MINIO_ENDPOINT,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=MINIO_SECURE
        )
        
        minio_client.list_buckets()
        logger.info("Successfully connected to MinIO!")
        
        if not minio_client.bucket_exists(BUCKET_NAME):
            minio_client.make_bucket(BUCKET_NAME)
            logger.info(f"Created bucket: {BUCKET_NAME}")
            
        return minio_client
    except S3Error as e:
        logger.error(f"MinIO connection error: {str(e)}")
        raise

def generate_image_url(cam_id):
    return f"{IMAGE_URL_BASE}?id={cam_id}"

def save_images_json_format_to_minio(cam_id, minio_client, interval=CAPTURE_INTERVAL):
    json_name = f"image_json_format_{cam_id}.json"
    image_documents = []

    while True:
        try:
            image_url = generate_image_url(cam_id)
            response = requests.get(image_url)

            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='JPEG')
                timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")

                image_base64 = base64.b64encode(image_bytes.getvalue()).decode('utf-8')

                image_document = {
                    'image_id': f"image_{timestamp_str}",
                    'url': image_url,
                    'image_base64': image_base64,
                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    'camera_id': cam_id
                }

                image_documents.append(image_document)
                json_bytes = io.BytesIO(json.dumps(image_documents).encode('utf-8'))

                minio_client.put_object(
                    BUCKET_NAME,
                    json_name,
                    json_bytes,
                    length=json_bytes.getbuffer().nbytes,
                    content_type='application/json'
                )

                logger.info(f"Camera {cam_id}: Saved image {image_document['url']} to {json_name}")
            else:
                logger.error(f"Camera {cam_id}: HTTP error {response.status_code}")

            time.sleep(interval)

        except Exception as e:
            logger.error(f"Camera {cam_id}: Error occurred - {str(e)}")
            time.sleep(interval)

def start_camera_threads(camera_ids, minio_client, interval):
    threads = []
    for cam_id in camera_ids:
        thread = threading.Thread(
            target=save_images_json_format_to_minio, 
            args=(cam_id, minio_client, interval)
        )
        thread.daemon = True
        threads.append(thread)
        thread.start()
        logger.info(f"Started thread for camera {cam_id}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stop")
        return

def main():
    try:
        minio_client = init_minio()
        start_camera_threads(CAMERA_IDS, minio_client, CAPTURE_INTERVAL)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")

if __name__ == "__main__":
    main()