#!/bin/bash

cp /data/datasets/Euroc/V2_01_easy/400p_Calibration/ImuParams.yaml /root/Kimera-VIO-fork/params/EurocMono/ImuParams.yaml
cp /data/datasets/Euroc/V2_01_easy/400p_Calibration/LeftCameraParams.yaml /root/Kimera-VIO-fork/params/EurocMono/LeftCameraParams.yaml
cp /data/datasets/Euroc/V2_01_easy/400p_Calibration/RightCameraParams.yaml /root/Kimera-VIO-fork/params/EurocMono/RightCameraParams.yaml

echo 'Files copied!'
