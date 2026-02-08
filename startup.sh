#!/bin/bash
set -e

cd /home/site/wwwroot

# Install dependencies - Azure Web App has pip available in PATH
pip install --upgrade pip
pip install -r requirements.txt

# Navigate to backend and start
cd backend
exec gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000
