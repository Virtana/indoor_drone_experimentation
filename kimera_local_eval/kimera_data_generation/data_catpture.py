#!/usr/bin/env python3

import numpy as np
import pandas as pd
import depthai as depthai
import os
import cv2
import json
import datetime
import shutil

from datetime import datetime
from datetime import timedelta
from scipy import interpolate

from typing import Tuple, List, Union


# The following function is used for tracking memory and cpu usage on the OAK-D.
def printSystemInformation(info):
    m = 1024 * 1024 # MiB
    print(f"Ddr used / total - {info.ddrMemoryUsage.used / m:.2f} / {info.ddrMemoryUsage.total / m:.2f} MiB")
    print(f"Cmx used / total - {info.cmxMemoryUsage.used / m:.2f} / {info.cmxMemoryUsage.total / m:.2f} MiB")
    print(f"LeonCss heap used / total - {info.leonCssMemoryUsage.used / m:.2f} / {info.leonCssMemoryUsage.total / m:.2f} MiB")
    print(f"LeonMss heap used / total - {info.leonMssMemoryUsage.used / m:.2f} / {info.leonMssMemoryUsage.total / m:.2f} MiB")
    t = info.chipTemperature
    print(f"Chip temperature - average: {t.average:.2f}, css: {t.css:.2f}, mss: {t.mss:.2f}, upa: {t.upa:.2f}, dss: {t.dss:.2f}")
    print(f"Cpu usage - Leon CSS: {info.leonCssCpuUsage.average * 100:.2f}%, Leon MSS: {info.leonMssCpuUsage.average * 100:.2f} %")
    print("----------------------------------------")


def create_pipeline(hz: int, fps: int, sensor_resolution: str) -> depthai.Pipeline:
    pipeline = depthai.Pipeline()

    # Define left camera node.
    monoLeft = pipeline.create(depthai.node.MonoCamera)
    # Left camera properties.
    monoLeft.setCamera("left")
    monoLeft.setResolution(sensor_resolution)
    monoLeft.setFps(fps)

    # Define node for IMU data.
    imu = pipeline.create(depthai.node.IMU)
    imu.enableIMUSensor([depthai.IMUSensor.ACCELEROMETER_RAW, depthai.IMUSensor.GYROSCOPE_RAW], hz)
    imu.setBatchReportThreshold(20)
    imu.setMaxBatchReports(20)

    # Linking Left Mono Camera.
    xout_left_cam = pipeline.create(depthai.node.XLinkOut)
    xout_left_cam.setStreamName("left")
    monoLeft.out.link(xout_left_cam.input)

    # Linking IMU.
    imu_out = pipeline.create(depthai.node.XLinkOut)
    imu_out.setStreamName("imu")
    imu.out.link(imu_out.input)

    # CPU USAGE NODE
    # Define source and output
    sysLog = pipeline.create(depthai.node.SystemLogger)
    linkOut = pipeline.create(depthai.node.XLinkOut)
    linkOut.setStreamName("sysinfo")
    # Properties
    sysLog.setRate(1)  # 1 Hz
    # Linking
    sysLog.out.link(linkOut.input)
    return pipeline


def time_delta_to_nano_secs(delta: float) -> float:
    return round(delta * 1000000000)


def extract_imu_data(imu_packet: depthai.IMUPacket) -> Tuple[List[float], Union[int], List[float], Union[int]]:
    acceleroValues = imu_packet.acceleroMeter
    gyroValues = imu_packet.gyroscope
    gyroTs = gyroValues.getTimestampDevice()
    acceleroTs = acceleroValues.getTimestampDevice()
    return [gyroValues.x, gyroValues.y, gyroValues.z], gyroTs, [acceleroValues.x, acceleroValues.y, acceleroValues.z], acceleroTs


def add_directories(output_dir_path: str) -> None:
    sub_directories = ["/cam0", "/cam1", "/imu0", "/cam0/data", "/cam1/data"]
    dirs_to_create = [output_dir_path + dir for dir in sub_directories]
    for dir_to_create in dirs_to_create:
        if not os.path.exists(dir_to_create):
            os.makedirs(dir_to_create)


def setup_output_directory(output_dir_path: str) -> bool:
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


def interpolate_data_corrected(df: pd.DataFrame, x_col: str, y_col: str, orig_timestamps: np.array) -> np.array:
    interpolated_values = []
    interpolated_values.append(df[y_col].values[0])
    for orig_timestamp in orig_timestamps[1:]:
        # print("Looking for: ", orig_timestamp)
        lower_bound_idx = df[df[x_col] <= orig_timestamp].index.max()
        upper_bound_idx = df[df[x_col] > orig_timestamp].index.min()
        if np.isnan(lower_bound_idx)==False and np.isnan(upper_bound_idx)==False:
            bounds_df = df.iloc[lower_bound_idx: upper_bound_idx+1]
            interpolation_fn = interpolate.interp1d(bounds_df[x_col].values, bounds_df[y_col].values, kind='linear')
            # print(interp_fn(orig_timestamp))
            interpolated_values.append(interpolation_fn(orig_timestamp))
        else:
            interpolated_values.append(-1)
    return interpolated_values


def transform_sensor_readings(df: pd.DataFrame, sensor_transforms: dict) -> None:
    sensor_cols = list(df.columns)[1:]
    for sensor_col, sensor_transform in zip(sensor_cols, list(sensor_transforms.values())):
        df[sensor_col] = df[sensor_col].values * sensor_transform


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

    # Load configuration data.
    with open('config.json') as f:
        config = json.load(f)
        f.close()
    sensor_resolution = eval(config["SENSOR_RESOLUTION"])
    imu_fps = config["IMU_FPS"]
    camera_fps = int(config["CAMERA_FPS"])
    max_frames = int(config["MAX_FRAMES"])
    sensor_transforms = {'x_trans': float(config["X_AXIS_TRANSFORM"]), 
                  'y_trans': float(config["Y_AXIS_TRANSFORM"]),
                  'z_trans': float(config["Z_AXIS_TRANSFORM"])
    }


    # Instantiate necessary variables for storage.
    curr_timestamp = timestamp_now
    cam_data = []
    gyroscope_data = []
    accelerometer_data = []
    num_frames_captured = 0
    device = depthai.Device()
    with device:
        # Setup pipeline. 
        # Note that by setting IMU hz to 200, we will be capturing and 250 hz and 200 hz for the accelerometer and gyroscope respectively. 
        device.startPipeline(create_pipeline(hz=imu_fps, fps=camera_fps, sensor_resolution=sensor_resolution))
        qSysInfo = device.getOutputQueue(name="sysinfo", maxSize=4, blocking=True)
        stream_names = ['imu', 'left']
        print("Starting capture. Press (q) to halt capture and exit the program.")
        while (num_frames_captured <= max_frames-1):
            # sysInfo = qSysInfo.get()
            # printSystemInformation(sysInfo)
            imu_message = device.getOutputQueue(stream_names[0], maxSize=500, blocking=True).tryGet()
            if imu_message is not None:
                for imu_packet in imu_message.packets:
                    gyroscope_datapoint, gyroscope_time, accelerometer_datapoint, accelerometer_time = extract_imu_data(imu_packet)
                    gyroscope_timestamp = time_delta_to_nano_secs((gyroscope_time + curr_timestamp).timestamp())
                    accelerometer_timestamp = time_delta_to_nano_secs((accelerometer_time + curr_timestamp).timestamp())
                    gyroscope_datapoint.insert(0, gyroscope_timestamp)
                    accelerometer_datapoint.insert(0, accelerometer_timestamp)
                    gyroscope_data.append(gyroscope_datapoint)
                    accelerometer_data.append(accelerometer_datapoint)

            cam_message = device.getOutputQueue(stream_names[1], maxSize=500, blocking=True).tryGet()
            if cam_message is not None:
                num_frames_captured += 1
                cv_frame = cam_message.getCvFrame()
                left_cam_timestamp = time_delta_to_nano_secs((cam_message.getTimestampDevice(depthai.CameraExposureOffset.MIDDLE) + curr_timestamp).timestamp())
                cv2.imshow("left", cv_frame)
                cv2.imwrite(f'{output_dir_path}/cam0/data/{left_cam_timestamp}.png', cv_frame)
                cv2.imwrite(f'{output_dir_path}/cam1/data/{left_cam_timestamp}.png', cv_frame)
                cam_data.append([left_cam_timestamp, f"{left_cam_timestamp}.png"])
                if num_frames_captured % 10 == 0:
                    print("\r", end="")
                    print(f"Approximate number of frames captured: {num_frames_captured}.", end="")

            if cv2.waitKey(1) == ord("q"):
                break
        
        print(f"\nTotal number of frames captured: {num_frames_captured}.")
        cam_df = pd.DataFrame(cam_data, columns = ["#timestamp [ns]", "filename"])
        cam_df.drop(cam_df.tail(1).index,inplace=True)
        cam_df.to_csv(f'{output_dir_path}/cam0/data.csv', index=False)
        cam_df.to_csv(f'{output_dir_path}/cam1/data.csv', index=False)

        gyroscope_columns = ["#timestamp [ns]", "w_RS_S_x [rad s^-1]", "w_RS_S_y [rad s^-1]", "w_RS_S_z [rad s^-1]"]
        gyroscope_df = pd.DataFrame(gyroscope_data, columns = gyroscope_columns)
        gyroscope_df.to_csv(f'{output_dir_path}/imu0/gyro_data_pre_transform.csv', index=False)
        # transform_sensor_readings(gyroscope_df, sensor_transforms)
        # gyroscope_df.to_csv(f'{output_dir_path}/imu0/gyro_data_post_transform.csv', index=False)

        accelerometer_columns = ["#timestamp [ns]", "a_RS_S_x [m s^-2]", "a_RS_S_y [m s^-2]", "a_RS_S_z [m s^-2]"]
        accelerometer_df = pd.DataFrame(accelerometer_data, columns = accelerometer_columns)
        accelerometer_df.to_csv(f'{output_dir_path}/imu0/acc_data_pre_transform.csv', index=False)
        # transform_sensor_readings(accelerometer_df, sensor_transforms)
        # accelerometer_df.to_csv(f'{output_dir_path}/imu0/acc_data_post_transform.csv', index=False)

        # Option 1: Interpolate on all of the accelerometer data. 
        # Option 2: If option 1 does not work we can backfill the accelerometer data before interpolation.

        x_col = "#timestamp [ns]"
        gyroscope_timestamps = gyroscope_df[x_col].values
        
        for y_col in accelerometer_columns[1:]:
            interpolated_data = interpolate_data_corrected(accelerometer_df, x_col, y_col, gyroscope_timestamps)
            accelerometer_df[y_col] = interpolated_data
            accelerometer_df[y_col] = accelerometer_df[y_col].apply(lambda x: f"{x:.5f}")
        accelerometer_df[x_col] = gyroscope_timestamps[0:len(interpolated_data)]

        accelerometer_df.to_csv(f'{output_dir_path}/imu0/acc_data_post_transform_interpolated.csv', index=False)
        
        accelerometer_df.drop(accelerometer_df.tail(1).index,inplace=True)
        gyroscope_df.drop(gyroscope_df.tail(1).index,inplace=True)
        imu_df = accelerometer_df.merge(gyroscope_df, left_on=x_col, right_on=x_col)
        
        # Ensuring that columns in the order Kimera-VIO expects!
        imu_df = imu_df[['#timestamp [ns]','w_RS_S_x [rad s^-1]', 'w_RS_S_y [rad s^-1]', 'w_RS_S_z [rad s^-1]', 'a_RS_S_x [m s^-2]', 
                            'a_RS_S_y [m s^-2]', 'a_RS_S_z [m s^-2]']]
        imu_df.to_csv(f'{output_dir_path}/imu0/data.csv', index=False)
        exit(0)