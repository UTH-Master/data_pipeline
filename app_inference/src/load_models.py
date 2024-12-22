from fastapi import HTTPException
import requests
import torch

def download_model(model_url):
    """Download a file from Google Drive."""
    response = requests.get(model_url)
    if response.status_code == 200:
        return response.content
    else:
        raise HTTPException(status_code=404, detail="Model file not found on Google Drive")

def load_yolov8_model(model_id=None):
    """Load the YOLOv8 model from a Google Drive shared link."""
    if not model_id:
        model_id = 'INITIAL_MODEL_FILE_ID'  # Replace with your default model file ID
    download_url = f"https://drive.google.com/uc?export=download&id={model_id}"
    
    # Download model
    model_data = download_model(download_url)
    
    # Assuming the model is a .pt file
    model_path = "yolov8_model.pt"
    with open(model_path, "wb") as f:
        f.write(model_data)
    
    # Load model
    model = torch.load(model_path)
    model.eval()  # Set the model to inference mode
    return model