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

function update_output_path () {
    sed -i "s|^OUTPUT_PATH=.*|OUTPUT_PATH=$1|" "$KIMERA_SCRIPT"
}

function configure_script () {
    update_ds_path $1
    update_log_state $2
    update_output_path $3
}

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

# First value for all arrays is the default
max_features=( 300 ) #250 200 150 100 )
feat_type_num=( 3 0 1 )
feat_type_name=( GFTT FAST ORB )
max_age=( 25 20 15 10 )
declare -A feat_type
feat_type[3]="GFTT"
feat_type[0]="FAST"
feat_type[1]="ORB"

function run_tests () {
    # This function runs the tests after the frontend/backend config changes 
    # are made. The input include the dataset of interest and the output path
    # for storing all logs/results.

    # $ds_path=$1
    # $log_path=$2
    mkdir -p $2
    configure_script $1 0 $2

    # Run script and save terminal log 
    $KIMERA_SCRIPT >> ${2}/terminal.log 2>&1

    # Run script + save cpu use
    /usr/bin/time -v $KIMERA_SCRIPT 2> ${2}/time.log
    
    # Run script and do not save terminal logs; save gt and traj logs
    configure_script $1 1 $2
    $KIMERA_SCRIPT

    # tar output logs
    tar -cvf ${2}.tar.gz ${2}
    rm -rf $2
}

# For a single VIO config, test with multiple datasets
for ds in "${DATASETS[@]}"
do
    ds_path=${HOME_DIR}/$ds
    
    # Varying max number front end features
    for value in "${max_features[@]}"
    do
        # Update the max feature value
        update_frontend_num maxFeaturesPerFrame $value
        # Generate output path for logs to be saved to
        log_path="${HOME_DIR}/output_logs_max_feat_${value}_${ds}"
        
        # Run tests and save data
        run_tests ${ds_path} ${log_path}
    done
    # Reset to default at the end
    update_frontend_num maxFeaturesPerFrame ${max_features[0]}

    # Varying the feature type
    for key in "${feat_type[@]}"
    do
        update_frontend_num feature_detector_type $feat_type[$key]
        log_path="${HOME_DIR}/output_logs_type_${key}_${ds}"

        run_tests ${ds_path} ${log_path}
    done    
    # Reset to default
    update_frontend_num feature_detector_type $feat_type["GFTT"]
done

# Updating backend configs