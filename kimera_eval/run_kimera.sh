#!/bin/bash

# This script is used to run Kimera-VIO on an iMX93 with various configurations

HOME_DIR='/home/root'
KIMERA_DIR=${HOME_DIR}/Kimera-VIO 

echo $HOME_DIR
echo $KIMERA_DIR

# ---------------------------------
# Helper functions
#----------------------------------

# Updating stereoVIOEuroc.bash
function update_log_state () {
    sed -i "s/^LOG_OUTPUT=[0-9]\+$/LOG_OUTPUT=$1/" stereoVIOEuroc.bash
}
update_log_state 0 

function update_ds_path () {
    sed -i "s/^DATASET_PATH=.*/DATASET_PATH=$1/" stereoVIOEuroc.bash
}
update_ds_path "\/home\/root\/V1_01_easy"

function update_output_path () {
    sed -i "s/^OUTPUT_PATH=.*/OUTPUT_PATH=$1/" stereoVIOEuroc.bash
}
update_output_path "\"..\/output_logs_orb\""

function configure_script () {
    update_ds_path $1
    update_log_state $2
    update_output_path $3
}

configure_script "\/home\/root\/V1_02_easy" 1 "\"..\/output_logs_v2_easy\""

# Updating frontend configs

# Updating backend configs