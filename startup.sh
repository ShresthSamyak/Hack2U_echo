#!/bin/bash
set -e

# Activate Azure's Python virtual environment
source /home/site/wwwroot/antenv/bin/activate

# Navigate to backend
cd /home/site/wwwroot/backend

# Install dependencies
pip install -r ../requirements.txt --quiet

# Start the app
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
