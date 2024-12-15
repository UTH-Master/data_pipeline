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
    version="1.0.0",
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

@app.get("/streams/{frame_id}", response_model=StreamResponse)
async def get_stream_frame(frame_id: str):
    try:
        frame = app.database[COLLECTION_STREAM_NAME].find_one({"frame_id": frame_id})
        if frame is None:
            raise HTTPException(
                status_code=404, 
                detail=f"Frame not found with frame_id: {frame_id}"
            )
        return frame
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))