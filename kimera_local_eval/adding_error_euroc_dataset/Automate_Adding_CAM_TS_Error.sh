#!/bin/bash

WRITE_FILES=1
MAX_JITTER=2_000
WORKING_DIR='/home/shiva/Datasets/V2_01_easy/V2_01_easy'

# Rename old data.csv files in cam0 and cam1 directories.
mv $WORKING_DIR/mav0/cam0/data.csv $WORKING_DIR/mav0/cam0/data_old.csv
mv $WORKING_DIR/mav0/cam1/data.csv $WORKING_DIR/mav0/cam1/data_old.csv

# Rename old image folders in cam0 and cam1 directories.
mv $WORKING_DIR/mav0/cam0/data $WORKING_DIR/mav0/cam0/data_old
mv $WORKING_DIR/mav0/cam1/data $WORKING_DIR/mav0/cam1/data_old

# Copy unmodified images from Euroc default folder.
cp -r $WORKING_DIR/mav0_euroc/cam0/data $WORKING_DIR/mav0/cam0/data
cp -r $WORKING_DIR/mav0_euroc/cam1/data $WORKING_DIR/mav0/cam1/data

# Add error to CAM timestamps.
CAMERA_TYPE='cam0'
python3 Downsample_Perturb_CAM_Data.py $WRITE_FILES $MAX_JITTER $WORKING_DIR $CAMERA_TYPE

CAMERA_TYPE='cam1'
python3 Downsample_Perturb_CAM_Data.py $WRITE_FILES $MAX_JITTER $WORKING_DIR $CAMERA_TYPE