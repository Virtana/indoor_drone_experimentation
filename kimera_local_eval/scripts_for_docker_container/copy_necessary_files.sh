#!/bin/bash

# Variables
CONTAINER_NAME="objective_heisenberg"

LOCAL_PATH="/home/shiva/GitRepos/indoor_drone_experimentation/kimera_local_eval"
CONTAINER_PATH="/root/Kimera-VIO/scripts"

main_path='/home/shiva/GitRepos/indoor_drone_experimentation/kimera_local_eval'

# Commands to copy from localhost to docker container.
docker cp "$LOCAL_PATH"/calibration "$CONTAINER_NAME":"$CONTAINER_PATH"
docker cp "$LOCAL_PATH"/scripts_for_docker_container/param_mods_5Hz.sh "$CONTAINER_NAME":"$CONTAINER_PATH"
docker cp "$LOCAL_PATH"/scripts_for_docker_container/execute_custom_dataset.sh "$CONTAINER_NAME":"$CONTAINER_PATH"
docker cp "$LOCAL_PATH"/scripts_for_docker_container/execute_euroc_dataset.sh "$CONTAINER_NAME":"$CONTAINER_PATH"
docker cp "$LOCAL_PATH"/scripts_for_docker_container/update_mono_params_custom_dataset.sh "$CONTAINER_NAME":"$CONTAINER_PATH"
docker cp "$LOCAL_PATH"/scripts_for_docker_container/update_mono_params_euroc_dataset.sh "$CONTAINER_NAME":"$CONTAINER_PATH"
# The following commands are necessary for experiments concerning tesing Kimera with varying errors added to the IMU timestamps.
# docker cp "$LOCAL_PATH"/scripts_for_docker_container/automate_runs_with_imu_ts_mods.sh "$CONTAINER_NAME":"$CONTAINER_PATH"
# docker cp "$LOCAL_PATH"/adding_error_euroc_dataset/Downsample_Perturb_IMU_Data.py "$CONTAINER_NAME":"$CONTAINER_PATH"