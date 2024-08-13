# import the necessary packages
import apriltag
import argparse
import glob
import cv2
import json
import os
import numpy as np
import pandas as pd
import depthai as depthai

from datetime import datetime


def get_args():
	# Construct the Argument Parser and Parse the arguments.
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--capture", type=str, required=True, help="Whether or not to perform data capture (Y/N)")
    args = vars(arg_parser.parse_args())
    return args


def extract_bounding_boxes(result):
	(ptA, ptB, ptC, ptD) = result.corners
	ptB = (int(ptB[0]), int(ptB[1]))
	ptC = (int(ptC[0]), int(ptC[1]))
	ptD = (int(ptD[0]), int(ptD[1]))
	ptA = (int(ptA[0]), int(ptA[1]))
	return (ptA, ptB, ptC, ptD)


def load_camera_calibration_data(filename):
	data = None
	with open(filename) as file_handler:
		data = json.load(file_handler)
		file_handler.close()
	# The data object is an array representing the three cameras on the OAK-D.
	# The stereo cameras are idendified by indicies 0 and 1; and the color camera is identified by index 2.

	if data is not None:
		color_camera_calibration = data['cameraData'][2][1]
		distortion_coeff = np.array(color_camera_calibration['distortionCoeff'])
		camera_matrix = np.array(color_camera_calibration['intrinsicMatrix'])
		return distortion_coeff, camera_matrix
	else:
		exit(1)


def create_pipeline(fps):
	# pipeline = depthai.Pipeline()
    # # Node for Camera data - 720p colour output.
	# cam_rgb = pipeline.create(depthai.node.ColorCamera)
	# cam_rgb.setBoardSocket(depthai.CameraBoardSocket.CAM_A)
	# cam_rgb.setResolution(depthai.ColorCameraProperties.SensorResolution.THE_1080_P)
	# # cam_rgb.setFps(fps)
	# # XLinkOut is a "way out" from the device. Any data you want to transfer to host need to be send via XLink
	# xout_rgb = pipeline.createXLinkOut()
	# xout_rgb.setStreamName("rgb")
	# xout_rgb.input.setBlocking(False)
	# xout_rgb.input.setQueueSize(1)
	# cam_rgb.preview.link(xout_rgb.input)
	pipeline = depthai.Pipeline()

	# Define source and output
	camRgb = pipeline.create(depthai.node.ColorCamera)
	xoutVideo = pipeline.create(depthai.node.XLinkOut)

	xoutVideo.setStreamName("rgb")

	# Properties
	camRgb.setBoardSocket(depthai.CameraBoardSocket.CAM_A)
	camRgb.setResolution(depthai.ColorCameraProperties.SensorResolution.THE_1080_P)
	camRgb.setVideoSize(1920, 1080)

	xoutVideo.input.setBlocking(False)
	xoutVideo.input.setQueueSize(1)

	# Linking
	camRgb.video.link(xoutVideo.input)
	return pipeline


def timeDeltaToMilliS(delta) -> float:
    return delta.total_seconds()*1000


def capture_save_images(pipeline, num_images_to_campture, output_dir_path):
	delay = 50
	device = depthai.Device()
	with device:
		device.startPipeline(pipeline)
        # To consume the device results, we get one output queue from the device, with stream names we assigned earlier
		q_rgb = device.getOutputQueue("rgb", maxSize=1, blocking=False)
		counter = 0
		cam_data = []
		while counter < num_images_to_campture + delay:
            # We try to fetch the data from nn/rgb queues. tryGet will return either the data packet or None if there isn't any
			in_rgb = q_rgb.tryGet()
			if in_rgb is not None:
				device_timestamp = in_rgb.getTimestampDevice()
                # If the packet from RGB camera is present, we're retrieving the frame in OpenCV format using getCvFrame
				frame = in_rgb.getCvFrame()
				if frame is not None:
					counter += 1
					cv2.imshow("preview", frame)
					if counter > delay:
						cv2.imwrite(f'{output_dir_path}/{counter}.png', frame)
						cam_data.append([timeDeltaToMilliS(device_timestamp), f"{counter}.png"])
            # At any time, you can press "q" and exit the main loop, therefore exiting the program itself
			# if cv2.waitKey(1) == ord('q'):
			# 	break
		cam_df = pd.DataFrame(cam_data, columns = ["#timestamp [ns]", "filename"])
		return cam_df
	

def process_images(images_for_processing_paths, april_tag_size, output_dir_path):
	data_to_add_df = {
		'number_of_april_tags': [],
		'image_points': [],
		'successes': [],
		'rotation_vectors': [],
		'translation_vectors': []
	}

	results_for_df = []

	for image_for_processing_path in images_for_processing_paths:

		# Load the input image and convert it to grayscale.
		image = cv2.imread(image_for_processing_path)
		image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

		options = apriltag.DetectorOptions(families="tag25h9")
		detector = apriltag.Detector(options)
		results = detector.detect(image_gray)
		if len(results) > 0:

			world_pts = np.array([[0, 0, 0], 
                      [april_tag_size, 0, 0], 
                      [april_tag_size, april_tag_size, 0], 
                      [0, april_tag_size, 0]])

			# world_pts = np.array([[-april_tag_size/2, april_tag_size/2, 0],
            #           [april_tag_size/2, april_tag_size/2, 0],
            #           [april_tag_size/2, -april_tag_size/2, 0],
            #           [-april_tag_size/2, -april_tag_size/2, 0]])

			world_pts = world_pts.astype('float32')

			# We will only have at most one AprilTag per frame.
			result = results[0]

			# Extract the bounding box (x, y)-coordinates for the AprilTag and convert each of the (x, y)-coordinate pairs to integers.
			image_points = np.array(extract_bounding_boxes(result))
			image_points = image_points.astype('float32')

			print("Image points are: ", image_points)

			(success, rotation_vector, translation_vector) = \
				cv2.solvePnP(objectPoints=world_pts, imagePoints=image_points, cameraMatrix=camera_matrix, distCoeffs=distortion_coeff)

			print((type(success), type(rotation_vector), translation_vector))

			imagePoints_world, _ = cv2.projectPoints(world_pts, rotation_vector, translation_vector, camera_matrix, distortion_coeff)

			for point in imagePoints_world:
				cv2.circle(image, tuple(point[0].astype(int)), 5, (0, 255, 0), -1)

			# Draw the center (x, y)-coordinates of the AprilTag
			(cX, cY) = (int(result.center[0]), int(result.center[1]))
			cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)

			# Draw the tag family on the image
			tagFamily = result.tag_family.decode("utf-8")
			cv2.putText(image, tagFamily, (int(image_points[0][0]), int(image_points[0][1]) - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

			image_filename = image_for_processing_path.split(".")[1].split("/")[-1]
			cv2.imwrite(f'{output_dir_path}/{image_filename}_identified.png', image)

			if success:
				results_for_df.append((success, np.array2string(rotation_vector), np.array2string(translation_vector)))
			else:
				results_for_df.append((0, -1, -1))
	return pd.DataFrame({'Success': [i[0] for i in results_for_df], 'r_vecs':[i[1] for i in results_for_df], 't_vecs':[i[2] for i in results_for_df]})



if __name__ == "__main__":
	args = get_args()

	print(args)

	# Load camera calibration data.
	calibration_filepath = "./Default_Calibration_Data/calib_18443010A177F50800.json"
	distortion_coeff, camera_matrix = load_camera_calibration_data(calibration_filepath)

	if args['capture'] == 'Y':
		# Get camera data.
		pipeline = create_pipeline(fps=1)

		# Get date and time for folder creation.
		now = datetime.now()
		dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")

		# Create target directory.
		output_dir_path = f"./Ground_Truth_Images/Results_{dt_string}_"
		os.makedirs(output_dir_path)

		# Connect to OAK-D and capture images.
		images_df = capture_save_images(pipeline=pipeline, num_images_to_campture=10, output_dir_path=output_dir_path)

	else:
		dt_string = '2024_08_13_09_05_47'
		output_dir_path = f"./Ground_Truth_Images/Results_{dt_string}_"
		images_df = pd.read_csv(f"{output_dir_path}/data.csv")

	# Run April-Tag detection and pose estimation.
	images_for_processing = glob.glob(f"{output_dir_path}/*.png")
	results_df = process_images(images_for_processing[0:1], 0.117/2, output_dir_path)

	# Add results(df_results) to cam_df!
	final_df = pd.concat([images_df, results_df], axis=1)
	final_df.to_csv(f'{output_dir_path}/data_pose.csv')

	