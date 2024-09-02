#!/usr/bin/env python3

import numpy as np
import pandas as pd
import depthai as depthai
import os
import cv2
import datetime
import shutil

from datetime import datetime
from datetime import timedelta

# Maximum numbers of camera frames that can be captured.
MAX_FRAMES = 1000


def create_pipeline(hz, fps):
    pipeline = depthai.Pipeline()

    # Define left camera node.
    monoLeft = pipeline.create(depthai.node.MonoCamera)
    # Left camera properties.
    monoLeft.setCamera("left")
    monoLeft.setResolution(depthai.MonoCameraProperties.SensorResolution.THE_400_P)
    monoLeft.setFps(fps)

    # Define node for IMU data.
    imu = pipeline.create(depthai.node.IMU)
    imu.enableIMUSensor([depthai.IMUSensor.ACCELEROMETER_RAW, depthai.IMUSensor.GYROSCOPE_RAW], hz)
    imu.setBatchReportThreshold(1)
    imu.setMaxBatchReports(10)

    # Linking Left Mono Camera.
    xout_left_cam = pipeline.create(depthai.node.XLinkOut)
    xout_left_cam.setStreamName("left")
    monoLeft.out.link(xout_left_cam.input)

    # Linking IMU.
    imu_out = pipeline.create(depthai.node.XLinkOut)
    imu_out.setStreamName("imu")
    imu.out.link(imu_out.input)

    return pipeline


def time_delta_to_nano_secs(delta) -> float:
    return round(delta * 1000000000)


def extract_imu_data(imu_packet):
    acceleroValues = imu_packet.acceleroMeter
    gyroValues = imu_packet.gyroscope
    return [gyroValues.x, gyroValues.y, gyroValues.z, acceleroValues.x, acceleroValues.y, acceleroValues.z]


def add_directories(output_dir_path):
    sub_directories = ["/cam0", "/cam1", "/imu0", "/cam0/data", "/cam1/data"]
    dirs_to_create = [output_dir_path + dir for dir in sub_directories]
    for dir_to_create in dirs_to_create:
        if not os.path.exists(dir_to_create):
            os.makedirs(dir_to_create)


def setup_output_directory(output_dir_path):
    if os.path.exists(output_dir_path):
        user_input = input("Output directory contains files. If (Y) this folder will be wiped. If (N) this program will exit and you can backup the folder. Enter (Y/N): ")
        if user_input.upper() == "Y":
            shutil.rmtree(output_dir_path)
            add_directories(output_dir_path)
            return True
        else:
            return False
    else:
        add_directories(output_dir_path)
        return True


if __name__ == "__main__":
    # Get date and time for folder creation.
    timestamp_now = datetime.now()
    dt_string = timestamp_now.strftime("%Y_%m_%d_%H_%M_%S")
    
    # Setup and create output directory path.
    output_dir_path = f"./Output/{dt_string}/mav0"
    dir_creation_result = setup_output_directory(output_dir_path)
    if dir_creation_result == False:
        print("Exiting program ...")
        exit()
    
    # Instantiate necessary variables for storage.
    curr_timestamp = timestamp_now
    cam_data = []
    imu_data = []
    counter = 0
    device = depthai.Device()
    with device:
        # Setup pipeline
        device.startPipeline(create_pipeline(hz=100, fps=4))
        stream_names = ['imu', 'left']
        print("Starting capture. Press (q) to halt capture and exit the program.")
        while True:
            for stream_name in stream_names:
                message = device.getOutputQueue(stream_name).tryGet()
                if message is not None:
                    if stream_name == 'imu':
                        imu_packets = message.packets
                        # print("Number of IMU packets:", len(imu_packets))
                        imu_packet = imu_packets[0]
                        imu_data_point = extract_imu_data(imu_packet)
                        imu_timestamp = time_delta_to_nano_secs((message.getTimestampDevice() + curr_timestamp).timestamp())
                        imu_data_point.insert(0, imu_timestamp)
                        imu_data.append(imu_data_point)
                    elif stream_name == 'left':
                        counter += 1
                        cv_frame = message.getCvFrame()
                        left_cam_timestamp = time_delta_to_nano_secs((message.getTimestampDevice(depthai.CameraExposureOffset.MIDDLE) + curr_timestamp).timestamp())
                        # left_cam_timestamp = time_delta_to_nano_secs((message.getTimestampDevice() + curr_timestamp).timestamp())
                        cv2.imshow("left", cv_frame)
                        cv2.imwrite(f'{output_dir_path}/cam0/data/{left_cam_timestamp}.png', cv_frame)
                        cv2.imwrite(f'{output_dir_path}/cam1/data/{left_cam_timestamp}.png', cv_frame)
                        cam_data.append([left_cam_timestamp, f"{left_cam_timestamp}.png"])

                    if counter % 10 == 0:
                        print("\r", end="")
                        print(f"Approximate number of frames captured: {counter}.", end="")

                if cv2.waitKey(1) == ord("q") or counter == MAX_FRAMES-1:
                    print(f"\nTotal number of frames captured: {counter}.")
                    cam_df = pd.DataFrame(cam_data, columns = ["#timestamp [ns]", "filename"])
                    cam_df.to_csv(f'{output_dir_path}/cam0/data.csv', index=False)
                    cam_df.to_csv(f'{output_dir_path}/cam1/data.csv', index=False)
                    imu_df = pd.DataFrame(imu_data, columns = ["#timestamp [ns]", "w_RS_S_x [rad s^-1]", "w_RS_S_y [rad s^-1]", "w_RS_S_z [rad s^-1]", "a_RS_S_x [m s^-2]", "a_RS_S_y [m s^-2]", "a_RS_S_z [m s^-2]"])
                    imu_df.to_csv(f'{output_dir_path}/imu0/data.csv', index=False)
                    exit(0)
        