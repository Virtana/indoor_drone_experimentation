#!/bin/bash

calibration_sub_dir="$1"

rm ../params/EurocMono/LeftCameraParams.yaml
rm ../params/EurocMono/RightCameraParams.yaml

cp ./calibration/Custom_Dataset/"${calibration_sub_dir}"p_Calibration/LeftCameraParams.yaml ../params/EurocMono/
cp ./calibration/Custom_Dataset/"${calibration_sub_dir}"p_Calibration/RightCameraParams.yaml ../params/EurocMono/