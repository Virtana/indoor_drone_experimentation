#!/usr/bin/env python3

import depthai as dai
import numpy as np
import sys
from pathlib import Path

# Connect Device
with dai.Device() as device:
    calibData = device.readCalibration()
    print(calibData.getDefaultIntrinsics(dai.CameraBoardSocket.CAM_A))
    # print(calibData.getCameraToImuExtrinsics(cameraId=dai.CameraBoardSocket.CAM_A, useSpecTranslation=False))
    # print(calibData.getCameraToImuExtrinsics(cameraId=dai.CameraBoardSocket.CAM_B, useSpecTranslation=False))
    print(calibData.getCameraToImuExtrinsics(cameraId=dai.CameraBoardSocket.CAM_C, useSpecTranslation=False))