#!/bin/bash
# Ground truth needs to be disabled in Kimera-VIO before executing!

# Set the keyframe rate.
./param_mods_4hz.sh

# Copy the relevant(based capture on resolution) parameter files for the OAK-D's cameras.
# The first parameter denotes the resolution (in pixels) our camera's images are captured at.
./update_mono_params_custom_dataset.sh 400

# Setup the directory for saving.
main_dir_name='Custom_Dataset'
experiment_dir_name='Dataset_2_20Hz_0.25_Keyframe'

mkdir data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name

# Execute Kimera-VIO and copy the output_logs directory.
./stereoVIOEuroc.bash
cp -r ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name