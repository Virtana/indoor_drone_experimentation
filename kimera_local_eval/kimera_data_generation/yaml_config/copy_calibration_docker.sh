#!/bin/bash

cp /data/datasets/Euroc/V2_01_easy/ImuParams.yaml /root/Kimera-VIO-fork/params/EurocMono/ImuParams.yaml
cp /data/datasets/Euroc/V2_01_easy/LeftCameraParams.yaml /root/Kimera-VIO-fork/params/EurocMono/LeftCameraParams.yaml
cp /data/datasets/Euroc/V2_01_easy/RightCameraParams.yaml /root/Kimera-VIO-fork/params/EurocMono/RightCameraParams.yaml

echo 'Files copied!'