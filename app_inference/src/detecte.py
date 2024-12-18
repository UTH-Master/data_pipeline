import cv2
from datetime import datetime
import uuid
from src.post_processing import line_intersection
from src.ultils import encode_image_to_base64
from config import VEHICLE_COUNTS, LIST_VEHICLE
def detecte_stream(stream, model, line_position):
    global stop_stream
    try:
        frame_count = 0
        while True:
            frame = stream.read()
            # if stop_stream:
            #     print("Stopping stream as per request.")
            #     break
            if frame is None:
                break
            if frame_count % 30 == 0:
                (h, w), new_width = frame.shape[:2], 640
                aspect_ratio = h / w
                new_height = int(new_width * aspect_ratio)
                frame = cv2.resize(frame, (new_width, new_height), interpolation = cv2.INTER_LINEAR)
                detections = model(frame, size=640)
   
                for *xyxy, conf, cls in detections.xyxy[0]:
                    name_value = detections.names[int(cls)]
                    if name_value  in LIST_VEHICLE:  
                        bbox = [int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3])]
                        if line_intersection(line_position, bbox):
                            unique_id = uuid.uuid4()
                            frame_info = {
                                "id": str(unique_id),
                                "time": datetime.now().isoformat(),
                                "vehicles": [],
                                "image": encode_image_to_base64(frame)
                            }
                            # car_count += 1
                            # cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 0, 255), 2)
                            # cv2.putText(frame, f'Car {car_count}', (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 2)
                            VEHICLE_COUNTS[name_value] += 1
                            frame_info["vehicles"].append({
                                "type": name_value,
                                "count": VEHICLE_COUNTS[name_value],
                                "bbox": bbox
                            })
                            print(frame_info)

                frame_count = 0
            frame_count += 1
    except KeyboardInterrupt:
        print("Stream stopped!")
    finally:
        stream.stop()