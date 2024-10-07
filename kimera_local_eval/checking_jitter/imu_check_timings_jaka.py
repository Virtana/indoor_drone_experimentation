import cv2
import depthai as dai
import numpy as np
import pandas as pd

from datetime import datetime
from datetime import timedelta

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

def time_delta_to_nano_secs(delta) -> float:
    return round(delta * 1000000000)

if __name__ == "__main__":

    # Steup constants.
    NUMBER_OF_DATA_PACKETS_TO_CAPTURE = 10000
    IMU_RATE = 250
    THRESHOLD_WARN = ((1000.0 / IMU_RATE) * 1.2) * 1000000 #Convert from ms to ns.
    print(f"THRESHOLD_WARN={THRESHOLD_WARN}")

    # Create pipeline
    pipeline = dai.Pipeline()

    # CPU USAGE NODE
    # Define source and output
    sysLog = pipeline.create(dai.node.SystemLogger)
    linkOut = pipeline.create(dai.node.XLinkOut)
    linkOut.setStreamName("sysinfo")
    # Properties
    sysLog.setRate(1)  # 1 Hz
    # Linking
    sysLog.out.link(linkOut.input)

    # IMU NODES
    # Define sources and outputs
    imu = pipeline.create(dai.node.IMU)
    xlinkOut = pipeline.create(dai.node.XLinkOut)
    pipeline.setXLinkChunkSize(0)
    xlinkOut.setStreamName("imu")
    # Enable GYROSCOPE_RAW at 200 Hz rate
    imu.enableIMUSensor(dai.IMUSensor.ACCELEROMETER_RAW, IMU_RATE)
    # Set batch report threshold and max batch reports
    imu.setBatchReportThreshold(1)
    imu.setMaxBatchReports(100)
    # Link plugins IMU -> XLINK
    imu.out.link(xlinkOut.input)

    # Initialize list to store time deltas
    time_deltas = []
    timestamps = []

    timestamp_now = datetime.now()
    curr_timestamp = timestamp_now

    # Pipeline is defined, now we can connect to the device
    with dai.Device(pipeline) as device:

        device.setLogLevel(dai.LogLevel.DEBUG)

        # Print MxID, USB speed, and available cameras on the device
        print('MxId:',device.getDeviceInfo().getMxId())
        print('USB speed:',device.getUsbSpeed())
        print('Connected cameras:',device.getConnectedCameras())

        # Output queue for imu bulk packets
        imuQueue = device.getOutputQueue(name="imu", maxSize=100, blocking=True)  # Reduce maxSize for more frequent updates
        lastTimestamp = None

        qSysInfo = device.getOutputQueue(name="sysinfo", maxSize=4, blocking=True)

        while len(time_deltas) < NUMBER_OF_DATA_PACKETS_TO_CAPTURE:
            
            sysInfo = qSysInfo.get()
            printSystemInformation(sysInfo)

            imuData: dai.IMUData = imuQueue.get()  # blocking call, will wait until new data has arrived
            currentTimestamp = time_delta_to_nano_secs((imuData.getTimestampDevice() + curr_timestamp).timestamp())
            # print(currentTimestamp)
        
            if lastTimestamp is not None:
                delta = (currentTimestamp - lastTimestamp)  # Calculate time delta
                time_deltas.append(delta)
                timestamps.append(currentTimestamp)
                print(f"delta timestamp: {delta} ns", end="\r")
                if (delta > THRESHOLD_WARN):
                    print(f"[warn] unusual delta timestamp > {delta} ns")

            lastTimestamp = currentTimestamp

    # Calculate mean and standard deviation
    time_deltas_ms = [x for x in time_deltas]


    df = pd.DataFrame(data = {'timestamp [ns]':timestamps, 'time_deltas [ns]': time_deltas})
    df.to_csv('jaka_script_imu.csv', index=False)