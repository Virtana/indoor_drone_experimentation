#!/bin/bash

# This script is used to run Kimera-VIO on an iMX93 with various configurations

HOME_DIR='/home/root'
KIMERA_DIR=${HOME_DIR}/Kimera-VIO
PARAMS_DIR=${KIMERA_DIR}/params/EurocMono
FRONTEND_CONF=${PARAMS_DIR}/FrontendParams.yaml
KIMERA_SCRIPT=${KIMERA_DIR}/scripts/stereoVIOEuroc.bash
# FRONTEND_CONF='params/FrontendParams.yaml'

DATASETS=( "V1_01_easy" ) #"V1_02_easy" "V1_01_medium" )

# ---------------------------------
# Helper functions
#----------------------------------

# Updating stereoVIOEuroc.bash
function update_log_state () {
    sed -i "s/^LOG_OUTPUT=[0-9]\+$/LOG_OUTPUT=$1/" $KIMERA_SCRIPT
}
# update_log_state 0 

function update_ds_path () {
    sed -i "s|^DATASET_PATH=.*|DATASET_PATH=$1|" "$KIMERA_SCRIPT"
}
# update_ds_path "\/home\/root\/V1_01_easy"

function update_output_path () {
    sed -i "s|^OUTPUT_PATH=.*|OUTPUT_PATH=$1|" "$KIMERA_SCRIPT"
}
# update_output_path "\"..\/output_logs_orb\""

function configure_script () {
    update_ds_path $1
    update_log_state $2
    update_output_path $3
}

# configure_script "\/home\/root\/V1_02_easy" 1 "\"..\/output_logs_v2_easy\""

function update_yaml_num () {
    # This function can be used to update the number value for a field 
    # in either the Frontend or Backend Params yaml files.
    # $1 is the filename, $2 is the field name and $3 is the field value
    sed -i "s/$2: [0-9]\+/$2: $3/" "$1"
}

# Testing with updating frontend configs
function update_frontend_num () {
    # $1 is field name, $2 is field value
    update_yaml_num $FRONTEND_CONF $1 $2
}

# function update_maxfeatures () {
#     update_frontend_num maxFeaturesPerFrame $1  
# }

# update_maxfeatures 250

# First value for all arrays is the default
max_features=( 300 ) #250 200 150 100 )
feat_type_num=( 3 0 1 )
feat_type_name=( GFTT FAST ORB )
max_age=( 25 20 15 10 )

for value in "${max_features[@]}"
do
    # Update the max feature value
    update_frontend_num maxFeaturesPerFrame $value

    # For a single VIO config, test with multiple datasets
    for ds in "${DATASETS[@]}"
    do
        # Configure script for running VIO
        ds_path=${HOME_DIR}/$ds
        log_path="${HOME_DIR}/output_logs_max_feat_${value}_${ds}"
        mkdir -p $log_path
        configure_script $ds_path 0 $log_path

        # Run script and save terminal log 
        $KIMERA_SCRIPT >> ${log_path}/terminal.log 2>&1

        # Run script + save cpu use
        /usr/bin/time -v $KIMERA_SCRIPT 2> ${log_path}/time.log
        
        # Run script and do not save terminal logs
        configure_script $ds_path 1 $log_path
        $KIMERA_SCRIPT

        # tar output logs
        tar -cvf ${log_path}.tar.gz ${log_path}
        rm -rf $log_path
    done

    # Run Kimera without logging, for each dataset, with 
done

# Updating backend configs