import cv2
import depthai as dai
import numpy as np
import pandas as pd

IMU_RATE = 200
THRESHOLD_WARN = (1000.0 / IMU_RATE) * 1.2
print(f"THRESHOLD_WARN={THRESHOLD_WARN}")

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
imu = pipeline.create(dai.node.IMU)
xlinkOut = pipeline.create(dai.node.XLinkOut)
pipeline.setXLinkChunkSize(0)

xlinkOut.setStreamName("imu")

# Enable GYROSCOPE_RAW at 200 Hz rate
imu.enableIMUSensor(dai.IMUSensor.ACCELEROMETER_RAW, IMU_RATE)

# Set batch report threshold and max batch reports
imu.setBatchReportThreshold(1)
imu.setMaxBatchReports(10)

# Link plugins IMU -> XLINK
imu.out.link(xlinkOut.input)

# Initialize list to store time deltas
time_deltas = []

# Pipeline is defined, now we can connect to the device
with dai.Device(pipeline) as device:

    device.setLogLevel(dai.LogLevel.DEBUG)

    # Print MxID, USB speed, and available cameras on the device
    print('MxId:',device.getDeviceInfo().getMxId())
    print('USB speed:',device.getUsbSpeed())
    print('Connected cameras:',device.getConnectedCameras())

    # Output queue for imu bulk packets
    imuQueue = device.getOutputQueue(name="imu", maxSize=20000, blocking=True)  # Reduce maxSize for more frequent updates
    lastTimestamp = None

    while len(time_deltas) < 10000:
        imuData: dai.IMUData = imuQueue.get()  # blocking call, will wait until new data has arrived
        currentTimestamp = imuData.getTimestamp().total_seconds()
    
        if lastTimestamp is not None:
            delta = (currentTimestamp - lastTimestamp)  # Calculate time delta
            delta *= 1000
            time_deltas.append(delta)
            tsF  = "{:.09f}"
            print(f"delta timestamp: {tsF.format(delta)} ms", end="\r")
            if (delta > THRESHOLD_WARN):
                print(f"[warn] unusual delta timestamp > {tsF.format(delta)} ms")

        lastTimestamp = currentTimestamp

# Calculate mean and standard deviation
time_deltas_ms = [x * 1000 for x in time_deltas]
mean_delta = np.mean(time_deltas_ms)
std_delta = np.std(time_deltas_ms)

df = pd.DataFrame(data = {'time_deltas_ms': time_deltas_ms, 'mean_delta':mean_delta, 'std_delta':std_delta})
df.to_csv('jaka_script_imu.csv')