#!/bin/bash

# Set the keyframe rate.
./param_mods_4hz.sh

# Copy the relevant parameter files for the MAV's cameras.
./update_mono_params_euroc_dataset.sh

# Setup the directory for saving.
main_dir_name='Euroc_Dataset'
experiment_dir_name='20Hz_0.25_Keyframe'

mkdir /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name

# Execute Kimera-VIO and copy the output_logs directory.
./stereoVIOEuroc.bash
cp -r ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name