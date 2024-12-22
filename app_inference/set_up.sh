#!/bin/bash

# Define the folder to remove and the git repository
FOLDER="ingest_data"
REPO_URL="https://github.com/UTH-Master/data_pipeline.git"
PYTHON_SCRIPT="autosaveytblivestream-mongodb.py" # The Python script you want to run

cd /home/km2401

# Step 1: Check for the virtual environment, create if it does not exist
if [ ! -d "env" ]; then
    echo "Creating Python3 virtual environment..."
    python3 -m venv env
fi

# Step 2: Activate the virtual environment
echo "Activating the virtual environment..."
source env/bin/activate

# Step 3: Remove the folder if it exists
if [ -d "$FOLDER" ]; then
    echo "Removing the folder: $FOLDER"
    rm -rf "$FOLDER"
fi

# Step 4: Clone the git repository
echo "Cloning the repository..."
git clone $REPO_URL $FOLDER

# Step 5: Install dependencies from requirements.txt
echo "Installing dependencies..."
pip3 install -r "$FOLDER/requirements.txt"

cd "$FOLDER/mongodb"
# Step 6: Run the Python script
echo "Running the Python script..."
python3 "$PYTHON_SCRIPT"

# Optional: Deactivate the virtual environment
echo "Deactivating the virtual environment..."
deactivate