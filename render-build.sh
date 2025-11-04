#!/usr/bin/env bash
set -o errexit

# Install ffmpeg safely
apt-get update
apt-get install -y ffmpeg

# Install Python packages
pip install -r requirements.txt
