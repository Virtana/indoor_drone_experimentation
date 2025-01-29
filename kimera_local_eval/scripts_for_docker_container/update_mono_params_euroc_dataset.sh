#!/bin/bash

rm ../params/EurocMono/LeftCameraParams.yaml
rm ../params/EurocMono/RightCameraParams.yaml

cp ./calibration/Euroc_Dataset/LeftCameraParams.yaml ../params/EurocMono/
cp ./calibration/Euroc_Dataset/RightCameraParams.yaml ../params/EurocMono/