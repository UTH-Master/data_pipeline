from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import torch
import uvicorn
from src.load_models import load_yolov8_model
from config import OPTIONS, URL, LINE_POSITION, SIGNAL_STOP
from vidgear.gears import VideoGear
import cv2
import threading
from datetime import datetime, timedelta
import uuid
from src.post_processing import line_intersection
from src.ultils import encode_image_to_base64
from config import  LIST_VEHICLE
from src.post_processing import insert_multiple_rows_from_dicts

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
    global SIGNAL_STOP 
    SIGNAL_STOP = False
    stream = VideoGear( source=URL, stream_mode=True,logging=True, **OPTIONS).start()
    detecte_stream(stream, model, LINE_POSITION)
    return {"message": "Stream started"}


@app.post("/stop-stream/")
def stop_streaming():
    global SIGNAL_STOP
    SIGNAL_STOP = True
    return {"message": "Stream stopping initiated"}


def detecte_stream(stream, model, line_position):
    try:
        frame_count = 0
        start_time = datetime.now()
        VEHICLE_COUNTS = {
            "car": 0,
            "motorcycle": 0,
            "bicycle": 0,
            "bus": 0,
            "truck": 0
        }
        while True:
            frame = stream.read()
            if SIGNAL_STOP:
                return 1
            if frame is None:
                break
            if frame_count % 30 == 0:
                # (h, w), new_width = frame.shape[:2], 640
                # aspect_ratio = h / w
                # new_height = int(new_width * aspect_ratio)
                # frame = cv2.resize(frame, (new_width, new_height), interpolation = cv2.INTER_LINEAR)
                detections = model(frame, size=640)
                
                for *xyxy, conf, cls in detections.xyxy[0]:
                    name_value = detections.names[int(cls)]
                    if name_value  in LIST_VEHICLE:  
                        bbox = [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])]
                        unique_id = uuid.uuid4()
                        if line_intersection(line_position, bbox): 
                            VEHICLE_COUNTS[name_value] += 1
                        frame_info = {
                            "id": str(unique_id),
                            "time": datetime.now().isoformat(),
                            "vehicles": [],
                            "image": encode_image_to_base64(frame)
                        }   
                frame_count = 0
            frame_count += 1
            if (datetime.now() - start_time) >= timedelta(seconds=10):
                vehicle_data = [{
                        "id": frame_info["id"],
                        "id_camera": "001",
                        "id_picture": "0001",
                        "img": frame_info["image"],
                        "count_car" : VEHICLE_COUNTS["car"],
                        "count_motorcycle" : VEHICLE_COUNTS["motorcycle"],
                        "count_bicycle" : VEHICLE_COUNTS["bicycle"],
                        "count_truck" : VEHICLE_COUNTS["truck"],
                        "count_all": sum(VEHICLE_COUNTS.values()),
                        "latitude": 16.07417144176758,
                        "longitude": 108.21640822331663,
                        "other": None,
                        "date": None,
                        "created_at": frame_info["time"]
                    }]
                print(vehicle_data)
                snapshot_thread = threading.Thread(target=snapshot_task, args=(vehicle_data,),daemon=True)
                snapshot_thread.start()
                frame_info = {}
                VEHICLE_COUNTS = {
                    "car": 0,
                    "motorcycle": 0,
                    "bicycle": 0,
                    "bus": 0,
                    "truck": 0
                }
                start_time = datetime.now()

    except KeyboardInterrupt:
        print("Stream stopped!")
    finally:
        stream.stop()
def snapshot_task(data_snapshot):
    try:
        insert_multiple_rows_from_dicts("report_traffic", data_snapshot)
    except Exception as e:
        print(f"Snapshot thread encountered an error: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
