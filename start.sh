#!/bin/bash

# Check Python virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi
if [ ! -f ".venv/bin/activate" ]; then
    echo "Activating Python virtual environment..."
    python3 -m venv .venv
fi
# Activate virtual environment
echo "Activating Python virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -r oddagent/requirements.txt

# Start the service
echo "Starting xiaoluo backend service..."
python3 -m oddagent.app
