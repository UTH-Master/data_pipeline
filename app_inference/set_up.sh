#!/bin/bash

# Define the folder to remove and the git repository
PYTHON_SCRIPT="main.py" 

# if [ -d "$FOLDER" ]; then
#     echo "Removing the folder: $FOLDER"
#     rm -rf "/home/km2401/data_pipeline"
# fi

# git clone https://github.com/UTH-Master/data_pipeline.git

# Step 1: Check for the virtual environment, create if it does not exist
if [ ! -d "env" ]; then
    echo "Creating Python3 virtual environment..."
    python3 -m venv env
fi

# Step 2: Activate the virtual environment
echo "Activating the virtual environment..."
source env/bin/activate

cd "/home/km2401/data_pipeline"
# # Step 4: Clone the git repository
git clone https://github.com/ultralytics/yolov5
pip install -r "yolov5/requirements.txt"

cd /home/km2401/data_pipeline/app_inference
# Step 5: Install dependencies from requirements.txt
echo "Installing dependencies..."
pip3 install -r "requirements.txt"

# Step 6: Run the Python script
echo "Running the Python script..."
python3 "$PYTHON_SCRIPT"

# Optional: Deactivate the virtual environment
echo "Deactivating the virtual environment..."
deactivate