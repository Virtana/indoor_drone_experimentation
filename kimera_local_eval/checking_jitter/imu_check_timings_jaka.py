import cv2
import depthai as dai
import numpy as np
import pandas as pd

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
imu = pipeline.create(dai.node.IMU)
xlinkOut = pipeline.create(dai.node.XLinkOut)
pipeline.setXLinkChunkSize(0)

xlinkOut.setStreamName("imu")

# Enable GYROSCOPE_RAW at 200 Hz rate
imu.enableIMUSensor(dai.IMUSensor.ACCELEROMETER_RAW, 100)

# Set batch report threshold and max batch reports
imu.setBatchReportThreshold(1)
imu.setMaxBatchReports(10)

# Link plugins IMU -> XLINK
imu.out.link(xlinkOut.input)

# Initialize list to store time deltas
time_deltas = []

# Pipeline is defined, now we can connect to the device
with dai.Device(pipeline) as device:

    # Output queue for imu bulk packets
    imuQueue = device.getOutputQueue(name="imu", maxSize=50, blocking=False)  # Reduce maxSize for more frequent updates
    lastTimestamp = None

    while len(time_deltas) < 10000:
        imuData: dai.IMUData = imuQueue.get()  # blocking call, will wait until new data has arrived
        currentTimestamp = imuData.getTimestamp().total_seconds()
    
        if lastTimestamp is not None:
            delta = (currentTimestamp - lastTimestamp)  # Calculate time delta
            time_deltas.append(delta)
            if (delta > 12.0):
                print(f"[warn] unusual delta timestamp > {tsF.format(timeDelta)} ms")

        lastTimestamp = currentTimestamp

# Calculate mean and standard deviation
time_deltas_ms = [x * 1000 for x in time_deltas]
mean_delta = np.mean(time_deltas_ms)
std_delta = np.std(time_deltas_ms)

df = pd.DataFrame(data = {'time_deltas_ms': time_deltas_ms, 'mean_delta':mean_delta, 'std_delta':std_delta})
df.to_csv('jaka_script_imu.csv')

# Create scatter plot
# plt.figure(figsize=(10, 6))
# plt.scatter(range(len(time_deltas_ms)), time_deltas_ms, c='blue', label='Time Deltas', s=10)
# plt.axhline(mean_delta, color='red', linestyle='--', label=f'Mean = {mean_delta:.2f} ms')
# plt.text(0, 0, f"Mean: {mean_delta:.2f} ms\nStd: {std_delta:.2f} ms", fontsize=12, bbox=dict(facecolor='white', alpha=0.5))
# plt.xlabel('Measurement Index')
# plt.ylabel('Time Delta (ms)')
# plt.title('Scatter Plot of Time Deltas Between Consecutive IMU Packets')
# plt.legend()
# plt.show()