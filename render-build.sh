#!/usr/bin/env bash
# render-build.sh

set -o errexit  # stop on error

# Create virtual environment (Render uses one automatically)
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Download static ffmpeg binary instead of using apt-get
echo "Downloading FFmpeg..."
mkdir -p ffmpeg-bin
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz
tar -xf ffmpeg.tar.xz --strip-components=1 -C ffmpeg-bin
export PATH="$PATH:$(pwd)/ffmpeg-bin"

echo "✅ Build complete."
