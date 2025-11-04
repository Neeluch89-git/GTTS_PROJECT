#!/usr/bin/env bash
set -o errexit

# Install ffmpeg for pydub audio processing
apt-get update -y && apt-get install -y ffmpeg
