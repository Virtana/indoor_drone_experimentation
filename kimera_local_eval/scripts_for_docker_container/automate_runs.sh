#!/bin/bash

main_dir_name='Uniform_Dist_Errors/Software_Timestamping_RTOS_IMU'

error_added='1us'

freq='6'
experiment_dir_name="${error_added}_${freq}Hz"
mkdir ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name
/bin/bash param_mods_6hz.sh
for i in {1..3}; 
do
    ./stereoVIOEuroc.bash
    cp -r ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name/$i
done

freq='4'
experiment_dir_name="${error_added}_${freq}Hz"
mkdir ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name
/bin/bash param_mods_4hz.sh
for i in {1..3}; 
do
    ./stereoVIOEuroc.bash
    cp -r ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name/$i
done