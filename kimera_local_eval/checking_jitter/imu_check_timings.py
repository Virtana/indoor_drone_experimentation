#!/usr/bin/env python3

import cv2
import depthai as dai
import time
import math

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
imu = pipeline.create(dai.node.IMU)
xlinkOut = pipeline.create(dai.node.XLinkOut)
pipeline.setXLinkChunkSize(0)

xlinkOut.setStreamName("imu")

IMU_RATE = 100
THRESHOLD_WARN = (1000.0 / IMU_RATE) * 1.2
print(f"THRESHOLD_WARN={THRESHOLD_WARN}")

SENSORS_TO_CAPTURE = [dai.IMUSensor.ACCELEROMETER_RAW, dai.IMUSensor.GYROSCOPE_RAW]

# enable ACCELEROMETER_RAW & GYROSCOPE_RAW at {IMU_RATE} hz rate
imu.enableIMUSensor(SENSORS_TO_CAPTURE[0], IMU_RATE)
# it's recommended to set both setBatchReportThreshold and setMaxBatchReports to 20 when integrating in a pipeline with a lot of input/output connections
# above this threshold packets will be sent in batch of X, if the host is not blocked and USB bandwidth is available
imu.setBatchReportThreshold(1)
# maximum number of IMU packets in a batch, if it's reached device will block sending until host can receive it
# if lower or equal to batchReportThreshold then the sending is always blocking on device
# useful to reduce device's CPU load  and number of lost packets, if CPU load is high on device side due to multiple nodes
imu.setMaxBatchReports(1)

# Link plugins IMU -> XLINK
imu.out.link(xlinkOut.input)

# Pipeline is defined, now we can connect to the device
with dai.Device(pipeline) as device, open('delta_time_accelerometer_100_1_1_1000Queue_JAKA.csv', 'w') as fileDeltaTime:
    fileDeltaTime.write(f"# delta timestamp (device) [us]\n")

    def timeDeltaToMilliS(delta) -> float:
        return delta.total_seconds()*1000

    # Output queue for imu bulk packets
    imuQueue = device.getOutputQueue(name="imu", maxSize=1000, blocking=True)
    baseTs = None
    while True:
        imuData = imuQueue.get()  # blocking call, will wait until a new data has arrived

        imuPackets = imuData.packets
        for imuPacket in imuPackets:

            acceleroValues = imuPacket.acceleroMeter
            #gyroValues = imuPacket.gyroscope

            acceleroTs = acceleroValues.getTimestampDevice()
            #gyroTs = gyroValues.getTimestampDevice()

            packetTs = min(acceleroTs, acceleroTs)
            if baseTs is None:
                baseTs = packetTs
            else:
                timeDelta = timeDeltaToMilliS(packetTs - baseTs)

                tsF  = "{:.03f}"
                print(f"delta timestamp: {tsF.format(timeDelta)} ms", end="\r")
                if (timeDelta > THRESHOLD_WARN):
                    print(f"[warn] unusual delta timestamp > {tsF.format(timeDelta)} ms")

                fileDeltaTime.write(f"{int(timeDelta * 1000)}\n")
                baseTs = packetTs

        # if cv2.waitKey(1) == ord('q'):
        #     break
