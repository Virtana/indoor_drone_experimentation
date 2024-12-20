#!/bin/bash

WRITE_FILES=1
MAX_JITTER=10_000
WORKING_DIR='/home/shiva/Datasets/V2_01_easy/V2_01_easy'

mv $WORKING_DIR/mav0/imu0/data.csv $WORKING_DIR/mav0/imu0/data_old.csv
python3 Downsample_Perturb_IMU_Data.py $WRITE_FILES $MAX_JITTER $WORKING_DIR