#!/bin/bash
source ~/miniconda3/etc/profile.d/conda.sh
conda create -n pomodoro python=3.10
conda activate pomodoro
pip install -r /path/to/requirements.txt
python /path/to/pomodoro.py