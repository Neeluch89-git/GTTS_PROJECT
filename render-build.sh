#!/usr/bin/env bash
# Install ffmpeg before Python dependencies
apt-get update && apt-get install -y ffmpeg
pip install -r requirements.txt
