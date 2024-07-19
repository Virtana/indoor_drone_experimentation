#!/usr/bin/env python3

import numpy as np
import pandas as pd
import cv2
import depthai as depthai
import datetime

from datetime import timedelta


def create_pipeline(hz, fps):
    pipeline = depthai.Pipeline()

    # Ensures syncing among all nodes within maximum millisecond threshold.
    sync = pipeline.create(depthai.node.Sync)
    sync.setSyncThreshold(timedelta(milliseconds=50))
    sync.setSyncAttempts(-1)

    xoutGrp = pipeline.create(depthai.node.XLinkOut)
    xoutGrp.setStreamName("xout")

    # Define left and right camera nodes
    monoLeft = pipeline.create(depthai.node.MonoCamera)
    monoRight = pipeline.create(depthai.node.MonoCamera)

    # Properties
    monoLeft.setCamera("left")
    monoLeft.setResolution(depthai.MonoCameraProperties.SensorResolution.THE_720_P)
    monoLeft.setFps(fps)
    monoRight.setCamera("right")
    monoRight.setResolution(depthai.MonoCameraProperties.SensorResolution.THE_720_P)
    monoLeft.setFps(fps)

    # Define node for IMU data.
    imu = pipeline.create(depthai.node.IMU)
    imu.enableIMUSensor([depthai.IMUSensor.ACCELEROMETER_RAW, depthai.IMUSensor.GYROSCOPE_RAW], hz)
    imu.setBatchReportThreshold(1)
    imu.setMaxBatchReports(10)

    # Attach nodes to sync node.
    monoLeft.out.link(sync.inputs["left_cam"])
    monoRight.out.link(sync.inputs["right_cam"])
    imu.out.link(sync.inputs["imu"])

    #Attach final node containing sync node to output.
    sync.out.link(xoutGrp.input)
    return pipeline


def get_avg_timestamp(groupMessage, curr_timestamp):
    node_message_names = groupMessage.getMessageNames()
    timedeltas = []
    for message_name in node_message_names:
        timedeltas.append(curr_timestamp + groupMessage[message_name].getTimestampDevice())
    return min(timedeltas).timestamp()


def timeDeltaToMilliS(delta) -> float:
        return delta.total_seconds()*1000


def extract_imu_data(imu_packet, baseTs):
    acceleroValues = imu_packet.acceleroMeter
    gyroValues = imu_packet.gyroscope

    # acceleroTs = acceleroValues.getTimestampDevice()
    # gyroTs = gyroValues.getTimestampDevice()
    # if baseTs is None:
    #     baseTs = acceleroTs if acceleroTs < gyroTs else gyroTs # We set baseTS to the smaller timestamp
    # acceleroTs = acceleroTs - baseTs
    # gyroTs = gyroTs - baseTs
    # imuF = "{:.06f}"
    # print(f"Accelerometer timestamp: {acceleroTs}")
    # print(f"Accelerometer [m/s^2]: x: {imuF.format(acceleroValues.x)} y: {imuF.format(acceleroValues.y)} z: {imuF.format(acceleroValues.z)}")
    # print(f"Gyroscope timestamp: {gyroTs}")
    # print(f"Gyroscope [rad/s]: x: {imuF.format(gyroValues.x)} y: {imuF.format(gyroValues.y)} z: {imuF.format(gyroValues.z)} ")

    return [gyroValues.x, gyroValues.y, gyroValues.z, acceleroValues.x, acceleroValues.y, acceleroValues.z]


if __name__ == "__main__":
    device = depthai.Device()
    node_message_names = ['imu', 'left_cam', 'right_cam']
    curr_timestamp = datetime.datetime.now()
    cam_data = []
    imu_data = []
    counter = 0
    with device:
        device.startPipeline(create_pipeline(15, 15))
        groupQueue = device.getOutputQueue("xout", 10, True)
        baseTs = None
        while True:
            groupMessage = groupQueue.get()
            imu_message = groupMessage["imu"]
            left_cam_message = groupMessage["left_cam"]
            right_cam_message = groupMessage["right_cam"]

            min_timestamp = get_avg_timestamp(groupMessage, curr_timestamp)
            # print(min_timestamp)

            imu_packets = imu_message.packets
            print("Number of IMU packets:", len(imu_packets))
            imu_packet = imu_packets[0]
            imu_data_point = extract_imu_data(imu_packet, baseTs)
            imu_data_point.insert(0, min_timestamp)
            imu_data.append(imu_data_point)

            cv2.imshow("left", left_cam_message.getCvFrame())
            cv2.imshow("right", right_cam_message.getCvFrame())

            cv2.imwrite(f'./Output/cam0/{counter}.png', left_cam_message.getCvFrame())
            cv2.imwrite(f'./Output/cam1/{counter}.png', right_cam_message.getCvFrame())

            cam_data.append([min_timestamp, f"{counter}.png"])

            counter += 1

            if cv2.waitKey(1) == ord("q"):
                cam_df = pd.DataFrame(cam_data, columns = ["#timestamp [ns]", "filename"])
                cam_df.to_csv('./Output/cam0/data.csv')
                cam_df.to_csv('./Output/cam1/data.csv')
                imu_df = pd.DataFrame(imu_data, columns = ["timestamp[ns]", "w_RS_S_x [rad s^-1]", "w_RS_S_y [rad s^-1]", "w_RS_S_z [rad s^-1]", "a_RS_S_x [m s^-2]", "a_RS_S_y [m s^-2]", "a_RS_S_z [m s^-2]"])
                imu_df.to_csv('./Output/imu0/data.csv')
                break