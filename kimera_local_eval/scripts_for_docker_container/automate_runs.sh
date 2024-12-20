#!/bin/bash

main_dir_name='Software_Timestamping_RTOS_IMU_V2'

error_added='2.5us'

freq='6'
experiment_dir_name="${error_added}_${freq}Hz"
mkdir ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name
/bin/bash 6hz.sh
for i in {1..3}; 
do
    ./stereoVIOEuroc.bash
    cp -r ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name/$i
done

freq='4'
experiment_dir_name="${error_added}_${freq}Hz"
mkdir ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name
/bin/bash 4hz.sh
for i in {1..3}; 
do
    ./stereoVIOEuroc.bash
    cp -r ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name/$i
done