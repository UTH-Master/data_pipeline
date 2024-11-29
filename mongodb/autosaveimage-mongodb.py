# Chu Duy Anh - 2480101001
# File chính để thu thập và lưu trữ ảnh từ camera vào MongoDB
# Chức năng:
# - Kết nối tới MongoDB server
# - Tạo các thread riêng cho từng camera
# - Thu thập ảnh từ các camera
# - Chuyển đổi ảnh sang dạng Base64 và lưu vào MongoDB collection
# - Ghi log theo dõi hoạt động hệ thống
# - Tự động xử lý lỗi và thử lại khi mất kết nối

import requests
import time
from datetime import datetime
from pymongo.mongo_client import MongoClient
import threading
import logging
import io
import base64
from PIL import Image
from config_mongodb import *

def setup_logging():
    logger = logging.getLogger(__name__)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    logger.setLevel(logging.INFO)
    logger.propagate = False
    
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.ERROR)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

logger = setup_logging()

running = True

def init_mongodb():
    try:
        client = MongoClient(MONGODB_URI)
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_IMAGE_NAME]
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        return client, db, collection
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        raise

def save_image_to_mongodb(cam_id, interval=CAPTURE_INTERVAL):
    global running
    while running:
        try:
            client, db, collection = init_mongodb()
            
            image_url = f"{IMAGE_URL_BASE}?id={cam_id}"
            response = requests.get(image_url)
            
            if response.status_code == 200:
                image = Image.open(io.BytesIO(response.content))
                image_bytes = io.BytesIO()
                image.save(image_bytes, format='JPEG')
                image_base64 = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
                
                timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
                
                image_document = {
                    'camera_id': cam_id,
                    'image_id': f"image_{timestamp_str}",
                    'url': image_url,
                    'type': 'camera',
                    'image_base64': image_base64,
                }

                result = collection.insert_one(image_document)
                logger.info(f"Camera {cam_id}: Saved image {image_document['image_id']}")
            else:
                logger.error(f"Camera {cam_id}: Failed to get image, status code: {response.status_code}")

            client.close()
            time.sleep(interval)

        except Exception as e:
            logger.error(f"Camera {cam_id}: Error occurred - {str(e)}")
            time.sleep(interval)
            
    logger.info(f"Camera {cam_id}: Thread stopped")

def start_camera_threads(camera_ids, collection, interval):
    global running
    threads = []
    for cam_id in camera_ids:
        thread = threading.Thread(
            target=save_image_to_mongodb,
            args=(cam_id, interval)
        )
        thread.daemon = True
        threads.append(thread)
        thread.start()
        logger.info(f"Started thread for camera {cam_id}")

    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping application...")
        running = False
        
        # Đợi tất cả thread kết thúc
        logger.info("Waiting for all threads to stop...")
        for thread in threads:
            thread.join(timeout=5)
        
        logger.info("All threads stopped")
        return

def main():
    global running
    try:
        client, db, collection = init_mongodb()
        start_camera_threads(CAMERA_IDS, collection, CAPTURE_INTERVAL)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
    finally:
        running = False
        if 'client' in locals():
            client.close()
            logger.info("MongoDB connection closed")

if __name__ == "__main__":
    main()
