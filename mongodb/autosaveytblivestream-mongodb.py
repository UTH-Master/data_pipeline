# Chu Duy Anh - 2480101001
# File chính để thu thập và lưu trữ luồng livestream từ YouTube vào MongoDB
# Chức năng:
# - Kết nối tới MongoDB server
# - Tạo các thread riêng cho từng luồng stream
# - Thu thập frames từ các luồng YouTube livestream
# - Chuyển đổi frame sang dạng Base64 và lưu vào MongoDB collection
# - Ghi log theo dõi hoạt động hệ thống
# - Tự động xử lý lỗi và thử lại khi mất kết nối

import cv2
import yt_dlp
import time
from datetime import datetime
from pymongo.mongo_client import MongoClient
import threading
import logging
import base64
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
        stream_collection = db[COLLECTION_STREAM_NAME]
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB!")
        return client, db, stream_collection
    except Exception as e:
        logger.error(f"MongoDB connection error: {str(e)}")
        raise

def get_youtube_stream(youtube_url):
    try:
        ydl_opts = {
            'format': 'best[height=720][ext=mp4]',
            'quiet': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(youtube_url, download=False)
            url = info['url']
            return cv2.VideoCapture(url)
    except Exception as e:
        logger.error(f"Error getting YouTube stream: {str(e)}")
        return None

def save_stream_to_mongodb(stream_id, youtube_url, interval=CAPTURE_STREAM_INTERVAL):
    global running
    while running:
        try:
            client, db, stream_collection = init_mongodb()
            
            cap = get_youtube_stream(youtube_url)
            if not cap:
                logger.error(f"Stream {stream_id}: Failed to open stream")
                time.sleep(interval)
                continue

            while cap.isOpened() and running:
                ret, frame = cap.read()
                if not ret:
                    break
                
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                current_timestamp = datetime.now()
                timestamp_str = current_timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")
                
                stream_document = {
                    'stream_id': stream_id,
                    'frame_id': f"frame_{timestamp_str}",
                    'url': youtube_url,
                    'type': 'stream',
                    'frame_base64': frame_base64,
                    'timestamp': current_timestamp
                }

                result = stream_collection.insert_one(stream_document)
                logger.info(f"Stream {stream_id}: Saved frame {stream_document['frame_id']}")

                time.sleep(interval)

            cap.release()
            client.close()

        except Exception as e:
            logger.error(f"Stream {stream_id}: Error occurred - {str(e)}")
            time.sleep(interval)
            
    logger.info(f"Stream {stream_id}: Thread stopped")

def start_stream_threads(stream_urls, stream_collection, interval):
    global running
    threads = []
    for stream_id, url in stream_urls.items():
        thread = threading.Thread(
            target=save_stream_to_mongodb,
            args=(stream_id, url, interval)
        )
        thread.daemon = True
        threads.append(thread)
        thread.start()
        logger.info(f"Started thread for stream {stream_id}")

    try:
        while running:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping application...")
        running = False
        
        logger.info("Waiting for all threads to stop...")
        for thread in threads:
            thread.join(timeout=5)
        
        logger.info("All threads stopped")
        return

def main():
    global running
    try:
        client, db, stream_collection = init_mongodb()
        start_stream_threads(YOUTUBE_STREAMS, stream_collection, CAPTURE_STREAM_INTERVAL)
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
    finally:
        running = False
        if 'client' in locals():
            client.close()
            logger.info("MongoDB connection closed")

if __name__ == "__main__":
    main()