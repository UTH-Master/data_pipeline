# Chu Duy Anh - 2480101001
# File API để đọc dữ liệu livestream và image từ MongoDB

import nest_asyncio
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pymongo import MongoClient
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from contextlib import asynccontextmanager
from mongodb.config_mongodb import *

# Models
class ImageResponse(BaseModel):
    camera_id: str
    image_id: str
    url: str
    type: str
    image_base64: str

class StreamResponse(BaseModel):
    stream_id: str
    frame_id: str
    url: str
    type: str
    frame_base64: str
    timestamp: datetime

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    app.mongodb_client = MongoClient(MONGODB_URI)
    app.database = app.mongodb_client[DATABASE_NAME]
    yield
    # Shutdown
    app.mongodb_client.close()

app = FastAPI(
    title="Camera Stream API",
    description="API để đọc dữ liệu livestream và image từ MongoDB",
    version="1.0.1",
    lifespan=lifespan
)

# API Endpoints

@app.get("/images/", response_model=List[ImageResponse])
async def get_images(
    camera_id: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100)
):
    try:
        query = {"type": "camera"}
        if camera_id:
            query["camera_id"] = camera_id

        images = list(app.database[COLLECTION_IMAGE_NAME].find(query).skip(skip).limit(limit))
        
        if not images:
            if camera_id:
                raise HTTPException(
                    status_code=404, 
                    detail=f"No images found for camera_id: {camera_id}"
                )
            else:
                raise HTTPException(
                    status_code=404, 
                    detail="No images found"
                )
                
        return images
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/images/{image_id}", response_model=ImageResponse)
async def get_image(image_id: str):
    try:
        image = app.database[COLLECTION_IMAGE_NAME].find_one({"image_id": image_id})
        if image is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Image not found with image_id: {image_id}"
            )
        return image
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/streams/", response_model=List[StreamResponse])
async def get_streams(
    stream_id: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=10, ge=1, le=100)
):
    try:
        query = {"type": "stream"}
        if stream_id:
            query["stream_id"] = stream_id

        streams = list(app.database[COLLECTION_STREAM_NAME].find(query).skip(skip).limit(limit))
        
        if not streams:
            if stream_id:
                raise HTTPException(
                    status_code=404, 
                    detail=f"No frames found for stream_id: {stream_id}"
                )
            else:
                raise HTTPException(
                    status_code=404, 
                    detail="No stream frames found"
                )
                
        return streams
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/streams/by-timestamp/", response_model=List[StreamResponse])
async def get_streams_by_timestamp(
    timestamp: str = Query(..., description="Timestamp format: YYYY-MM-DD (e.g. 2024-12-29)"),
    stream_id: Optional[str] = None,
    limit: int = Query(default=100, ge=1, le=1000)
):
    """
    Lấy danh sách frames từ một ngày cụ thể
    - timestamp: Ngày bắt đầu (format: YYYY-MM-DD)
    - stream_id: ID của stream (optional)
    - limit: Số lượng frame tối đa trả về
    """
    try:
        # Chuyển đổi timestamp string thành datetime object
        try:
            full_timestamp = f"{timestamp}T00:00:00.000000"
            timestamp_dt = datetime.strptime(full_timestamp, "%Y-%m-%dT%H:%M:%S.%f")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid timestamp format. Use YYYY-MM-DD (e.g. 2024-11-29)"
            )

        query = {
            "type": "stream",
            "timestamp": {"$gte": timestamp_dt}
        }
        
        if stream_id:
            query["stream_id"] = stream_id

        streams = list(app.database[COLLECTION_STREAM_NAME]
                      .find(query)
                      .sort("timestamp", 1)
                      .limit(limit))
        
        if not streams:
            if stream_id:
                raise HTTPException(
                    status_code=404,
                    detail=f"No frames found for stream_id: {stream_id} after {timestamp}"
                )
            else:
                raise HTTPException(
                    status_code=404,
                    detail=f"No frames found after {timestamp}"
                )

        return streams

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
    
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)