import requests
import time
from datetime import datetime
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import io
from PIL import Image
import hashlib
import pymongo
import threading
import logging
from config-mongodb import *

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))

# Config logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def init_mongodb():
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        images_collection = db[COLLECTION_NAME]
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        return client, db, images_collection
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        raise

def generate_image_url(cam_id):
    return f"{IMAGE_URL_BASE}?id={cam_id}"

def save_images_to_mongodb(cam_id, images_collection, interval=CAPTURE_INTERVAL):
    while True:
        try:
            image_url = generate_image_url(cam_id)
            response = requests.get(image_url)

            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='JPEG')
                timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")

                image_document = {
                    'image_id': f"image_{timestamp_str}",
                    'url': image_url,
                    'image_base64': image_bytes.getvalue(),
                }

                result = images_collection.insert_one(image_document)
                logger.info(f"Camera {cam_id}: Saved image {image_document['url']} to MongoDB")
            else:
                logger.error(f"Camera {cam_id}: HTTP error {response.status_code}")

            time.sleep(interval)

        except Exception as e:
            logger.error(f"Camera {cam_id}: Error occurred - {str(e)}")
            time.sleep(interval)

def start_camera_threads(camera_ids, images_collection, interval):
    threads = []
    for cam_id in camera_ids:
        thread = threading.Thread(
            target=save_images_to_mongodb, 
            args=(cam_id, images_collection, interval)
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
        client, db, images_collection = init_mongodb()
        start_camera_threads(CAMERA_IDS, images_collection, CAPTURE_INTERVAL)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()
            logger.info("MongoDB connection closed")

if __name__ == "__main__":
    main()