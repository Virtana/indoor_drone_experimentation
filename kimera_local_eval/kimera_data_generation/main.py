# Useful links:
# - https://docs.luxonis.com/software/depthai/examples/imu_accelerometer_gyroscope/
# - https://github.com/luxonis/depthai-experiments/blob/master/gen2-syncing/host-rgb-depth-sync.py


# Imports
from pathlib import Path

import cv2
import depthai
import numpy as np

from datetime import timedelta


def create_pipeline():
    pipeline = depthai.Pipeline()
    
    # Node for IMU data - We are capturing ACCELEROMETER_RAW and GYROSCOPE_RAW at 100 hz rate.
    imu = pipeline.create(depthai.node.IMU)
    imu.enableIMUSensor([depthai.IMUSensor.ACCELEROMETER_RAW, depthai.IMUSensor.GYROSCOPE_RAW], 100)
    # Above this threshold packets will be sent in batch of X, if the host is not blocked and USB bandwidth is available
    imu.setBatchReportThreshold(1)
    # Maximum number of IMU packets in a batch, if it's reached device will block sending until host can receive it
    # If lower or equal to batchReportThreshold then the sending is always blocking on device
    # useful to reduce device's CPU load  and number of lost packets, if CPU load is high on device side due to multiple nodes
    imu.setMaxBatchReports(10)
    xout_imu = pipeline.create(depthai.node.XLinkOut)
    xout_imu.setStreamName("imu")
    # Link plugins IMU -> XLINK
    imu.out.link(xout_imu.input)

    # Node for Camera data - 480p colour output.
    cam_rgb = pipeline.createColorCamera()
    cam_rgb.setPreviewSize(640, 480)
    cam_rgb.setInterleaved(False)
    # XLinkOut is a "way out" from the device. Any data you want to transfer to host need to be send via XLink
    xout_rgb = pipeline.createXLinkOut()
    xout_rgb.setStreamName("rgb")
    cam_rgb.preview.link(xout_rgb.input)

    return pipeline



if __name__ == "__main__":
    pipeline = create_pipeline()


    # We are using context manager here that will dispose the device after we stop using it
    with depthai.Device(pipeline) as device:

        def timeDeltaToMilliS(delta) -> float:
            return delta.total_seconds()*1000
        
        baseTs = None

        # From this point, the Device will be in "running" mode and will start sending data via XLink

        # To consume the device results, we get one output queue from the device, with stream names we assigned earlier
        q_rgb = device.getOutputQueue("rgb")
        q_imu = device.getOutputQueue("imu", maxSize=50, blocking=False)

        # Here, some of the default values are defined. Frame will be an image from "rgb" stream
        frame = None

        # Since the detections returned by nn have values from <0..1> range, they need to be multiplied by frame width/height to
        # receive the actual position of the bounding box on the image
        def frameNorm(frame, bbox):
            normVals = np.full(len(bbox), frame.shape[0])
            normVals[::2] = frame.shape[1]
            return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)


        while True:
            # We try to fetch the data from nn/rgb queues. tryGet will return either the data packet or None if there isn't any
            in_rgb = q_rgb.tryGet()
            in_imu = q_imu.tryGet()

            if in_imu is not None:
                imuPackets = in_imu.packets
                for imuPacket in imuPackets:
                    acceleroValues = imuPacket.acceleroMeter
                    gyroValues = imuPacket.gyroscope

                    acceleroTs = acceleroValues.getTimestampDevice()
                    gyroTs = gyroValues.getTimestampDevice()
                    if baseTs is None:
                        baseTs = acceleroTs if acceleroTs < gyroTs else gyroTs
                    acceleroTs = timeDeltaToMilliS(acceleroTs - baseTs)
                    gyroTs = timeDeltaToMilliS(gyroTs - baseTs)

                    imuF = "{:.06f}"
                    tsF  = "{:.03f}"

                    print(f"Accelerometer timestamp: {tsF.format(acceleroTs)} ms")
                    print(f"Accelerometer [m/s^2]: x: {imuF.format(acceleroValues.x)} y: {imuF.format(acceleroValues.y)} z: {imuF.format(acceleroValues.z)}")
                    print(f"Gyroscope timestamp: {tsF.format(gyroTs)} ms")
                    print(f"Gyroscope [rad/s]: x: {imuF.format(gyroValues.x)} y: {imuF.format(gyroValues.y)} z: {imuF.format(gyroValues.z)} ")

            if in_rgb is not None:
                # If the packet from RGB camera is present, we're retrieving the frame in OpenCV format using getCvFrame
                frame = in_rgb.getCvFrame()

            if frame is not None:
                cv2.imshow("preview", frame)

            # At any time, you can press "q" and exit the main loop, therefore exiting the program itself
            if cv2.waitKey(1) == ord('q'):
                break

