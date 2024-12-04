#!/bin/bash

folder_name=''

# Loop through numbers 1 to 10
for i in {1..3}; 
do
    ./stereoVIOEuroc.bash
    cp -r ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$folder_name/$i
done
