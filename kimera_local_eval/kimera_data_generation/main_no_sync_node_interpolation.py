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

# Maximum numbers of camera frames that can be captured.
MAX_FRAMES = 10000


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

def create_pipeline(hz, fps, sensor_resolution):
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


def time_delta_to_nano_secs(delta) -> float:
    return round(delta * 1000000000)


def extract_imu_data(imu_packet):
    acceleroValues = imu_packet.acceleroMeter
    gyroValues = imu_packet.gyroscope
    gyroTs = gyroValues.getTimestampDevice()
    acceleroTs = acceleroValues.getTimestampDevice()
    return [gyroValues.x, gyroValues.y, gyroValues.z], gyroTs, [acceleroValues.x, acceleroValues.y, acceleroValues.z], acceleroTs


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
    

def generate_interpolated_timestamps_v1(df, x_col, step):
    return np.arange(df[x_col].iloc[0], df[x_col].iloc[-1] + step, step)


def generate_interpolated_timestamps_v2(df, x_col, step):
    return df[x_col].values


def interpolate_data(df, x_col, y_col, start_stop_range):
    interpolated_data = np.interp(start_stop_range, df[x_col], df[y_col])
    return interpolated_data[0: df.shape[0]]


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

    # Load configuration.
    with open('config.json') as f:
        config = json.load(f)
        f.close()
    sensor_resolution = eval(config["SENSOR_RESOLUTION"])
    imu_fps = config["IMU_FPS"]
    camera_fps = int(config["CAMERA_FPS"])

    # Instantiate necessary variables for storage.
    curr_timestamp = timestamp_now
    cam_data = []
    gyroscope_data = []
    accelerometer_data = []
    counter = 0
    device = depthai.Device()
    with device:
        # Setup pipeline. 
        # Note that by setting IMU hz to 200, we will be capturing and 250 hz and 200 hz for the accelerometer and gyroscope respectively. 
        device.startPipeline(create_pipeline(hz=imu_fps, fps=camera_fps, sensor_resolution=sensor_resolution))
        qSysInfo = device.getOutputQueue(name="sysinfo", maxSize=4, blocking=True)
        stream_names = ['imu', 'left']
        print("Starting capture. Press (q) to halt capture and exit the program.")
        while True:
            # sysInfo = qSysInfo.get()
            # printSystemInformation(sysInfo)
            for stream_name in stream_names:
                message = device.getOutputQueue(stream_name, maxSize=500, blocking=True).tryGet()
                if message is not None:
                    if stream_name == 'imu':
                        for imu_packet in message.packets:
                            # TODO: Ensure that accelerometer and gyroscope data are extracted separately.
                            gyroscope_datapoint, gyroscope_time, accelerometer_datapoint, accelerometer_time = extract_imu_data(imu_packet)
                            gyroscope_timestamp = time_delta_to_nano_secs((gyroscope_time + curr_timestamp).timestamp())
                            accelerometer_timestamp = time_delta_to_nano_secs((accelerometer_time + curr_timestamp).timestamp())
                            gyroscope_datapoint.insert(0, gyroscope_timestamp)
                            accelerometer_datapoint.insert(0, accelerometer_timestamp)
                            gyroscope_data.append(gyroscope_datapoint)
                            accelerometer_data.append(accelerometer_datapoint)
                    elif stream_name == 'left':
                        counter += 1
                        cv_frame = message.getCvFrame()
                        left_cam_timestamp = time_delta_to_nano_secs((message.getTimestampDevice(depthai.CameraExposureOffset.MIDDLE) + curr_timestamp).timestamp())
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

                    gyroscope_df = pd.DataFrame(gyroscope_data, columns = ["#timestamp [ns]", "w_RS_S_x [rad s^-1]", "w_RS_S_y [rad s^-1]", "w_RS_S_z [rad s^-1]"])
                    gyroscope_df.to_csv(f'{output_dir_path}/imu0/gyro_data.csv', index=False)

                    accelerometer_df = pd.DataFrame(accelerometer_data, columns = ["#timestamp [ns]", "a_RS_S_x [m s^-2]", "a_RS_S_y [m s^-2]", "a_RS_S_z [m s^-2]"])
                    accelerometer_df.to_csv(f'{output_dir_path}/imu0/acc_data.csv', index=False)
                    timestamp_deltas = np.array([0])
                    timestamp_deltas = np.append(timestamp_deltas, np.diff(accelerometer_df['#timestamp [ns]'].values))
                    accelerometer_df['raw_timestamp'] = timestamp_deltas
                    accelerometer_df = accelerometer_df[accelerometer_df['raw_timestamp'] < np.mean(timestamp_deltas) + (1.5 * np.std(timestamp_deltas))]
                    accelerometer_df.to_csv(f'{output_dir_path}/imu0/acc_data_before_interpolation.csv', index=False)
                    accelerometer_df.drop(columns=['raw_timestamp'], inplace=True)


                    x_col = "#timestamp [ns]"
                    columns_to_interpolate = ["a_RS_S_x [m s^-2]", "a_RS_S_y [m s^-2]", "a_RS_S_z [m s^-2]"]
                    interpolated_timestamps = generate_interpolated_timestamps_v2(gyroscope_df, x_col, 10000000)
                    
                    for y_col in columns_to_interpolate:
                        interpolated_data = interpolate_data(accelerometer_df, x_col, y_col, interpolated_timestamps)
                        accelerometer_df[y_col] = interpolated_data
                    accelerometer_df[x_col] = interpolated_timestamps[0:interpolated_data.shape[0]]

                    accelerometer_df.to_csv(f'{output_dir_path}/imu0/acc_data_after_interpolation.csv', index=False)

                    imu_df = accelerometer_df.merge(gyroscope_df, left_on=x_col, right_on=x_col)
                    imu_df.to_csv(f'{output_dir_path}/imu0/data.csv', index=False)
                    exit(0)
        