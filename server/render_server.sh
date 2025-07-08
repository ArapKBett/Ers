#!/bin/bash
echo "Setting up server on Render..."
cd server
pip install -r requirements.txt
gunicorn --bind 0.0.0.0:$PORT c2_server:app
