#!/bin/bash
# Ground truth needs to be disabled in Kimera-VIO before executing!

# Set the keyframe rate as well as other important variables.
./param_mods_5Hz.sh

# Copy the relevant(based capture on resolution) parameter files for the OAK-D's cameras.
# The first parameter denotes the resolution (in pixels) our camera's images are captured at.
./update_mono_params_custom_dataset.sh Custom_Dataset_OpenCV_Calibration 720

# Setup the directory for saving.
main_dir_name='Custom_Dataset'
experiment_dir_name='Home_Office_720p_20Hz_0.25_Keyframe_Custom_Calibration'

mkdir data/datasets/Euroc/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name

# Execute Kimera-VIO and copy the output_logs directory.
./stereoVIOEuroc.bash
cp -r ../output_logs/* /data/datasets/Euroc/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name