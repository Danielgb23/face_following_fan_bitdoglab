#!/bin/bash
# This script is specific for my machine. Use it as a reference to setup the environment
pyenv shell  3.10.17
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install mediapipe opencv-python numpy
