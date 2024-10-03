# import the necessary packages
import apriltag
import argparse
import glob
import cv2
import json
import os
import copy
import numpy as np
import pandas as pd
import depthai as depthai
from scipy.spatial import distance

from datetime import datetime


def get_args():
	# Construct the Argument Parser and Parse the arguments.
	arg_parser = argparse.ArgumentParser()
	arg_parser.add_argument("--capture", type=str, required=True, help="Whether or not to perform data capture (Y/N)")
	arg_parser.add_argument("--kimera_data", type=str, required=True, help="Whether or not csv file has the  Kimera (Y/N)")
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
		color_camera_calibration = data['cameraData'][0][1]
		distortion_coeff = np.array(color_camera_calibration['distortionCoeff'])
		print(distortion_coeff)
		camera_matrix = np.array(color_camera_calibration['intrinsicMatrix'])
		camera_calibration_resolution = (color_camera_calibration['height'], color_camera_calibration['width'])
		return distortion_coeff, camera_matrix, camera_calibration_resolution
	else:
		exit(1)


def create_pipeline(fps, sensor_resolution):
	pipeline = depthai.Pipeline()

	mono_left_cam = pipeline.create(depthai.node.MonoCamera)

	# Properties
	mono_left_cam.setCamera("left")
	mono_left_cam.setResolution(sensor_resolution)
	mono_left_cam.setFps(fps)

	# Define source and output
	xoutVideo = pipeline.create(depthai.node.XLinkOut)
	xoutVideo.setStreamName("left_cam")

	xoutVideo.input.setBlocking(False)
	xoutVideo.input.setQueueSize(1)

	# Linking
	mono_left_cam.out.link(xoutVideo.input)
	return pipeline


def timeDeltaToMilliS(delta) -> float:
    return delta.total_seconds()*1000


def determine_scaling_factor(camera_calibration_resolution, image_size):
	height_scale = image_size[0]/camera_calibration_resolution[0]
	width_scale = image_size[1]/camera_calibration_resolution[1]
	print(camera_calibration_resolution)
	print(image_size)
	return (height_scale, width_scale)



def capture_save_images(pipeline, num_images_to_capture, output_dir_path, delay):
	device = depthai.Device()
	with device:
		device.startPipeline(pipeline)
        # To consume the device results, we get one output queue from the device, with stream names we assigned earlier
		mono_left_cam = device.getOutputQueue("left_cam", maxSize=1, blocking=False)
		counter = 0
		cam_data = []
		while counter < num_images_to_capture + delay:
            # We try to fetch the data from nn/rgb queues. tryGet will return either the data packet or None if there isn't any
			input_left_mono_cam = mono_left_cam.tryGet()
			if input_left_mono_cam is not None:
				device_timestamp = input_left_mono_cam.getTimestampDevice()
                # If the packet from RGB camera is present, we're retrieving the frame in OpenCV format using getCvFrame
				frame = input_left_mono_cam.getCvFrame()
				if frame is not None:
					counter += 1
					print("\r", end="")
					print(f"Approximate number of frames captured: {counter}.", end="")
					cv2.imshow("preview", frame)
					if counter > delay:
						cv2.imwrite(f'{output_dir_path}/{counter}.png', frame)
						cam_data.append([timeDeltaToMilliS(device_timestamp), f"{counter}.png"])
            # At any time, you can press "q" and exit the main loop, therefore exiting the program itself
			if cv2.waitKey(1) == ord('q'):
				break
		cam_df = pd.DataFrame(cam_data, columns = ["#timestamp [ns]", "filename"])
		return cam_df
	

def detect_apriltag_compute_pose(images_for_processing_paths, april_tag_size, output_dir_path, camera_calibration_resolution):
	data_to_add_df = {
		'number_of_april_tags': [],
		'image_points': [],
		'successes': [],
		'rotation_vectors': [],
		'translation_vectors': []
	}

	results_for_df = []

	for image_for_processing_path in images_for_processing_paths[0:1]:

		# Load the input image and convert it to grayscale.
		image = cv2.imread(image_for_processing_path)
		image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		image_size = image.shape
		height_scaling_factor_, width_scaling_factor_ = determine_scaling_factor(camera_calibration_resolution, image_size)
		print(f"Scaling factor applied: H: {height_scaling_factor_}, W: {width_scaling_factor_}")

		options = apriltag.DetectorOptions(families="tag25h9")
		detector = apriltag.Detector(options)
		results = detector.detect(image_gray)
		if len(results) > 0:

			# Axis centered on the top left corner,
			# Positive X to the right, positive Y down.
			world_pts = np.array([[0, 0, 0], 
                      [april_tag_size, 0, 0], 
                      [april_tag_size, april_tag_size, 0], 
                      [0, april_tag_size, 0]])

			world_pts = world_pts.astype('float32')

			# We will only have at most one AprilTag per frame.
			result = results[0]

			# Extract the bounding box (x, y)-coordinates for the AprilTag and convert each of the (x, y)-coordinate pairs to integers.
			image_points = np.array(extract_bounding_boxes(result))
			image_points = image_points.astype('float32')

			# camera_matrix_adjusted = copy.deepcopy(camera_matrix)
			# camera_matrix_adjusted[0][0] *= height_scaling_factor_
			# camera_matrix_adjusted[0][2] = image_size[1] / 2
			# camera_matrix_adjusted[1][1] *= width_scaling_factor_
			# camera_matrix_adjusted[1][2] = image_size[0] / 2

			camera_matrix_adjusted = copy.deepcopy(camera_matrix)
			camera_matrix_adjusted[0][0] *= width_scaling_factor_
			camera_matrix_adjusted[0][2] *= width_scaling_factor_
			camera_matrix_adjusted[1][1] *= height_scaling_factor_
			camera_matrix_adjusted[1][2] *= height_scaling_factor_
			print(camera_matrix_adjusted)

			(solve_pnp_success_result, rotation_vector, translation_vector) = \
				cv2.solvePnP(objectPoints=world_pts, imagePoints=image_points, cameraMatrix=camera_matrix_adjusted, distCoeffs=distortion_coeff)

			if solve_pnp_success_result:
				
				imagePoints_world, _ = cv2.projectPoints(world_pts, rotation_vector, translation_vector, camera_matrix_adjusted, distortion_coeff)
				
				total_error = 0.0
				for detected_point, projected_point in zip(image_points, imagePoints_world):
					print("April Tag Detected Points: ", detected_point)
					print("Projected April Tag Points: ", projected_point[0])
					error = distance.euclidean(detected_point, projected_point[0])
					print("Error: ", error)
					total_error += error
					print("-----------")
				print("Average Pixel Error: ", total_error/4)

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

				results_for_df.append((solve_pnp_success_result, np.array_repr(rotation_vector), np.array_repr(translation_vector), total_error/4))
			else:
				results_for_df.append((solve_pnp_success_result, -1, -1, -1))
	return pd.DataFrame({'success': [i[0] for i in results_for_df], 
					     'r_vecs_GT':[i[1] for i in results_for_df], 
						 't_vecs_GT':[i[2] for i in results_for_df],
						 'avg_pixel_error':[i[3] for i in results_for_df]})



if __name__ == "__main__":
	# Load arguements.
	args = get_args()

	# Load configuration.
	with open('config.json') as f:
		config = json.load(f)
		f.close()
	
	calibration_filepath = config["CALIBRATION_FILE_PATH"]
	main_directory = config["WORKING_DIRECTORY"]
	fps = int(config["FPS"])
	delay = int(config["DELAY"])
	num_images_to_capture = int(config["NUMBER_OF_IMAGES_TO_CAPTURE"])
	sensor_resolution = eval(config["SENSOR_RESOLUTION"])
	april_tag_size = float(config["APRIL_TAG_SIZE"])

	# Load camera calibration data.
	distortion_coeff, camera_matrix, camera_calibration_resolution = load_camera_calibration_data(calibration_filepath)

	if args['capture'] == 'Y':
		# Get camera data.
		pipeline = create_pipeline(fps, sensor_resolution)

		# Get date and time for folder creation.
		now = datetime.now()
		dt_string = now.strftime("%Y_%m_%d_%H_%M_%S")

		# Create target directory.
		output_dir_path = f"{main_directory}/Results_{dt_string}_"
		os.makedirs(output_dir_path)

		# Connect to OAK-D and capture images.
		images_df = capture_save_images(pipeline=pipeline, num_images_to_capture=num_images_to_capture, output_dir_path=output_dir_path, delay=delay)

	else:
		# Get all directories with data we can process.
		all_sub_directories = list(os.walk(main_directory))[1:]
		print("Subdirectory listing: ")
		for index, directory in enumerate(all_sub_directories):
			print(f'{index+1}. {directory[0]}')
		
		# Capture selection from user.
		selection = int(input(f"Enter the directory you would like to run AprilTag detection on ([{1}-{index+1}]): "))
		if selection >=1 or selection <= len(all_sub_directories):
			dt_string = all_sub_directories[selection-1][0].split('/')[2]
			print("Operating on:", dt_string)
			output_dir_path = f"{main_directory}/{dt_string}"
			images_df = pd.read_csv(f"{output_dir_path}/data.csv")
			# If this directory already contains files which identify the AprilTags, we can remove them.
			files_for_deletion = glob.glob(f"{output_dir_path}/*_identified.png")
			for file_to_delete in files_for_deletion:
				os.remove(file_to_delete)
			# For handling csv file with Kimera data headers.
			if args['kimera_data'] == 'Y':
				all_cols_to_drop = ['success', 'r_vecs_GT', 't_vecs_GT', 'avg_pixel_error']
				cols_to_drop = set(all_cols_to_drop).intersection(set(images_df.columns))
				images_df.drop(columns = cols_to_drop, inplace=True)
				images_df.to_csv(f"{output_dir_path}/data.csv", index=False)
		else:
			print("Invalid selection. Program will now exit.")
			exit(1)

	# Run April-Tag detection and pose estimation. 
	# NOTE: Images_for_processing is not in any particular order.
	images_for_processing = glob.glob(f"{output_dir_path}/*.png")
	results_df = detect_apriltag_compute_pose(images_for_processing_paths=images_for_processing, 
										   	  april_tag_size=april_tag_size, 
											  output_dir_path=output_dir_path, 
											  camera_calibration_resolution=camera_calibration_resolution)

	# Add results(df_results) to cam_df!
	final_df = pd.concat([images_df, results_df], axis=1)
	final_df.to_csv(f'{output_dir_path}/data_pose.csv', index=False)