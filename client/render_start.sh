#!/bin/bash
# Install required system packages
apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
pip install -r requirements.txt

# Start the client
python client.py
