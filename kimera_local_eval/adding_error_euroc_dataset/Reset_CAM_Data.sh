#!/bin/bash

WORKING_DIR='/home/shiva/Datasets/V2_01_easy/V2_01_easy'

# Remove existing data (images and .csv file)
rm -rf $WORKING_DIR/mav0/cam0
rm -rf $WORKING_DIR/mav0/cam1


# # Copy unmodified images from Euroc default folder.
cp -r $WORKING_DIR/mav0_euroc/cam0/ $WORKING_DIR/mav0/cam0/
cp -r $WORKING_DIR/mav0_euroc/cam1/ $WORKING_DIR/mav0/cam1/