#!/bin/sh

source ~/anaconda3/etc/profile.d/conda.sh
conda activate google-calendar-slack
sleep 5s
python3 /home/ec2-user/google-calendar-slack/main.py
