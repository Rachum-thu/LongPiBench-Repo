#!/bin/bash

# Step 1: Download the data.zip file
DATA_URL="https://github.com/Rachum-thu/LongPiBench-Repo/releases/download/release_1/data.zip"
DATA_DIR="data"
ZIP_FILE="data.zip"

# Download the file
if [ ! -f "$ZIP_FILE" ]; then
  echo "Downloading data.zip from $DATA_URL..."
  curl -L -o "$ZIP_FILE" "$DATA_URL"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to download data.zip"
    exit 1
  fi
else
  echo "data.zip already exists. Skipping download."
fi

# Step 2: Unzip the file and rename the folder
if [ -d "$DATA_DIR" ]; then
  echo "Data folder already exists. Skipping extraction."
else
  echo "Extracting $ZIP_FILE..."
  unzip "$ZIP_FILE" -d ./
  mv $(basename "$ZIP_FILE" .zip) "$DATA_DIR"
  if [ $? -ne 0 ]; then
    echo "Error: Failed to extract and rename data directory"
    exit 1
  fi
fi

# Step 3: Install dependencies
if [ -f "requirements.txt" ]; then
  echo "Installing dependencies from requirements.txt..."
  pip install -r requirements.txt
  if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies"
    exit 1
  fi
else
  echo "Error: requirements.txt not found"
  exit 1
fi

# Final Step: Notify the user of successful setup
echo "Setup completed successfully!"
echo "Please make sure to update the .env file with your API key and base URL."
