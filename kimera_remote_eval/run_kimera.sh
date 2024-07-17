#!/bin/bash

# This script is used to run Kimera-VIO on an iMX93 with various configurations

HOME_DIR='/home/root'
KIMERA_DIR=${HOME_DIR}/Kimera-VIO
PARAMS_DIR=${KIMERA_DIR}/params/EurocMono
FRONTEND_CONF=${PARAMS_DIR}/FrontendParams.yaml
BACKEND_CONF=${PARAMS_DIR}/BackendParams.yaml
KIMERA_SCRIPT=${KIMERA_DIR}/scripts/stereoVIOEuroc.bash

DATASETS=( "V1_01_easy"  "V2_01_easy" "V1_02_medium" )

# ---------------------------------
# Helper functions
#----------------------------------
# Updating stereoVIOEuroc.bash
function update_log_state () {
    sed -i "s/^LOG_OUTPUT=[0-9]\+$/LOG_OUTPUT=$1/" $KIMERA_SCRIPT
}

function update_ds_path () {
    sed -i "s|^DATASET_PATH=.*|DATASET_PATH=$1|" "$KIMERA_SCRIPT"
}

function update_output_path () {
    sed -i "s|^OUTPUT_PATH=.*|OUTPUT_PATH=$1|" "$KIMERA_SCRIPT"
}

function enable_lcd () {
    if [[ "$1" = true ]]; then
        sed -i "s|^USE_LCD=.*|USE_LCD=1|" "$KIMERA_SCRIPT"
    elif [[ "$1" = false ]]; then
        sed -i "s|^USE_LCD=.*|USE_LCD=0|" "$KIMERA_SCRIPT"
    else
        echo "Error with LCD option"
    fi
}

function enable_errlogs () {
    if [[ "$1" = true ]]; then
        sed -i "s|^--logtostderr=.*|--logtostderr=1|" "$KIMERA_SCRIPT"
    elif [[ "$1" = false ]]; then
        sed -i "s|^--logtostderr=.*|--logtostderr=0|" "$KIMERA_SCRIPT"
    else
        echo "Invalid input argument for function enable_errlogs"
    fi
}

function configure_script () {
    update_ds_path $1
    update_log_state $2
    update_output_path $3
    enable_errlogs $4
    enable_lcd false
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

function update_backend_num () {
    # $1 is field name, $2 is field value
    update_yaml_num $BACKEND_CONF $1 $2
}

function run_tests () {
    # This function runs the tests after the frontend/backend config changes 
    # are made. The input include the dataset of interest and the output path
    # for storing all logs/results.
    mkdir -p $2
    configure_script $1 0 $2 true

    # Run script and save terminal log 
    $KIMERA_SCRIPT >> ${2}/terminal.log 2>&1

    # Run script + save cpu use
    configure_script $1 0 $2 false
    /usr/bin/time -v $KIMERA_SCRIPT 2> ${2}/time.log
    
    # Run script and do not save terminal logs; save gt and traj logs
    configure_script $1 1 $2 false
    $KIMERA_SCRIPT

    # tar output logs
    tar -cvf ${2}.tar.gz ${2}
    rm -rf $2
}

# Frontend config options
#----------------------------
# First value for all arrays is the default
max_features=( 300 250 200 150 100 )
max_age=( 25 20 15 10 )

declare -A feat_type
feat_type[3]="GFTT"
feat_type[0]="FAST"
feat_type[1]="ORB"

# Backend config options
#-----------------------------
declare -A linearization_modes
linearization_modes[3]="jacobian_svd"
linearization_modes[2]="jacobian_q"
linearization_modes[1]="implicit_schur"
linearization_modes[0]="hessian"

horizon=( 6 5 4 3 ) # in seconds

# Before running any tests, reset everything we are changing to the default values.
update_frontend_num maxFeaturesPerFrame ${max_features[0]}
update_frontend_num feature_detector_type 3
update_frontend_num maxFeatureAge ${max_age[0]}
update_backend_num linearizationMode 0 #default
update_backend_num horizon ${horizon[0]}

# For a single VIO config, test with multiple datasets
for ds in "${DATASETS[@]}"
do
    ds_path=${HOME_DIR}/$ds
    echo "------------------- DATASET: ${ds} ----------------------"
    # -------------------------------------------
    #          FRONTEND CONFIG CHANGES
    # -------------------------------------------
    echo "---------------------MAX FEATURES----------------------------"
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

    echo "----------------------FEATURE TYPE---------------------------"
    # Varying the feature type
    for key in "${!feat_type[@]}"
    do
        update_frontend_num feature_detector_type ${key}
        log_path="${HOME_DIR}/output_logs_type_${feat_type[$key]}_${ds}"

        run_tests ${ds_path} ${log_path}
    done
    # Reset to default
    update_frontend_num feature_detector_type 3

    echo "------------------------MAX AGE------------------------------"
    # Varying the maxFeatureAge
    for value in "${max_age[@]}"
    do
        update_frontend_num maxFeatureAge $value
        log_path="${HOME_DIR}/output_logs_max_age_${value}_${ds}"

        run_tests ${ds_path} ${log_path}
    done
    update_frontend_num maxFeatureAge ${max_age[0]}

    # -------------------------------------------
    #          BACKEND CONFIG CHANGES
    # -------------------------------------------
    echo "------------------LINERIZATION MODE--------------------------"
    # Varying the linearizationMode
    for key in "${!linearization_modes[@]}"
    do
        update_backend_num linearizationMode ${key}
        log_path="${HOME_DIR}/output_logs_linmode_${linearization_modes[$key]}_${ds}"
        run_tests ${ds_path} ${log_path}
    done
    update_backend_num linearizationMode 0 #default

    echo "------------------------HORIZON--------------------------------"
    for value in "${horizon[@]}"
    do
        update_backend_num horizon $value
        log_path="${HOME_DIR}/output_logs_horizon_${value}_${ds}"
        run_tests ${ds_path} ${log_path}
    done
    update_backend_num horizon ${horizon[0]}

    # --------------------------------------------------------------------
    # Testing with Optimized case based on results from the previous tests
    # --------------------------------------------------------------------
    update_frontend_num feature_detector_type 0 # FAST
    update_frontend_num maxFeatureAge 15
    update_frontend_num maxFeaturesPerFrame 200
    update_backend_num linearizationMode 1 # implicit schur

    log_path="${HOME_DIR}/output_logs_FAST_schur_maxfeat200_maxage15_${ds}"
    run_tests ${ds_path} ${log_path}

    update_frontend_num feature_detector_type 0 # FAST
    update_frontend_num maxFeatureAge 15
    update_frontend_num maxFeaturesPerFrame 100
    update_backend_num linearizationMode 1 # implicit schur
    update_backend_num horizon 6

    log_path="${HOME_DIR}/output_logs_FAST_schur_maxfeat100_maxage15_${ds}"
    run_tests ${ds_path} ${log_path}
done
