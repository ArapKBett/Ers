#!/bin/bash
echo "Setting up client on Render..."
cd client
apt-get update && apt-get install -y iproute2 || true
python client_web.py
