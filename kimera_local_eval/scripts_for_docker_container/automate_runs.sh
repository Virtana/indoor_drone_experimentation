#!/bin/bash

main_dir_name='Software_Timestamping_RTOS_IMU'
experiment_dir_name='IMU_Error_0.0025ms_6Hz_Frame'


# Loop through numbers 1 to 10
for i in {1..3}; 
do
    ./stereoVIOEuroc.bash
    cp -r ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name/$i
done
