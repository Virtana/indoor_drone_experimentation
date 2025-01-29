#!/bin/bash

# Ensure that the python script (Downsample_Perturb_IMU_Data) is copier over!

max_errors=(1000 2500 5000 7500 10000 50000 100000)

for max_error_ns in "${max_errors[@]}"; do
    # Converting nanoseconds to microseconds.
    echo "Running experiments with: $max_error_ns ns."
    max_error_us=$(awk "BEGIN {print $max_error_ns / 1000}")

    # User specifies the main directory.
    main_dir_name='Gaussian_Dist_Errors/Software_Timestamping_RTOS_IMU_Between_Minus_Positive'

    # Adding error to IMU data based on $max_error_ns.
    WRITE_FILES=1
    MAX_JITTER=$max_error_ns
    WORKING_DIR='/data/datasets/Euroc/V2_01_easy'
    mv $WORKING_DIR/mav0/imu0/data.csv $WORKING_DIR/mav0/imu0/data_old.csv
    python3 Downsample_Perturb_IMU_Data.py $WRITE_FILES $MAX_JITTER $WORKING_DIR

    # Conducting 6Hz experiments.
    freq='6'
    experiment_dir_name="${max_error_us}us_${freq}Hz"
    mkdir /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name
    /bin/bash param_mods_6hz.sh
    for i in {1..3}; 
    do
        ./stereoVIOEuroc.bash
        cp -r ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name/$i
    done

    # Conducting 4Hz experiments.
    freq='4'
    experiment_dir_name="${max_error_us}us_${freq}Hz"
    mkdir /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name
    /bin/bash param_mods_4hz.sh
    for i in {1..3}; 
    do
        ./stereoVIOEuroc.bash
        cp -r ../output_logs /data/datasets/Euroc/V2_01_easy/Kimera_VIO_Output/$main_dir_name/$experiment_dir_name/$i
    done
done