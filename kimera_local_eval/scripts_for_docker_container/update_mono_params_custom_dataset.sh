#!/bin/bash

calibration_main_dir="$1"
calibration_sub_dir="$2"

rm ../params/EurocMono/LeftCameraParams.yaml
rm ../params/EurocMono/RightCameraParams.yaml
rm ../params/EurocMono/ImuParams.yaml

cp ./calibration/"${calibration_main_dir}"/"${calibration_sub_dir}"p_Calibration/LeftCameraParams.yaml ../params/EurocMono/
cp ./calibration/"${calibration_main_dir}"/"${calibration_sub_dir}"p_Calibration/RightCameraParams.yaml ../params/EurocMono/
cp ./calibration/"${calibration_main_dir}"/ImuParams.yaml ../params/EurocMono/