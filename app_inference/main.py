from fastapi import FastAPI, File, UploadFile 
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import torch
import uvicorn
from src.load_models import load_yolov8_model
from config import OPTIONS, URL, LINE_POSITION
from src.detecte import detecte_stream
from vidgear.gears import VideoGear

stop_stream = False

app = FastAPI(title="YOLOv8 Object Detection API")

class ModelUpdateRequest(BaseModel):
    model_id: str 

model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

@app.post("/load_new_version/")
async def load_new_version(request: ModelUpdateRequest):
    global model
    try:
        model = load_yolov8_model(request.model_id)
        return {"message": "Model updated successfully"}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": str(e)})

@app.post("/start-stream/")
def start_stream():
    global stop_stream
    stop_stream = False
    stream = VideoGear( source=URL, stream_mode=True,logging=True, **OPTIONS).start()
    detecte_stream(stream, model, LINE_POSITION)
    return {"message": "Stream started"}


@app.post("/stop-stream/")
def stop_streaming():
    global stop_stream
    stop_stream = True
    return {"message": "Stream stopping initiated"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
