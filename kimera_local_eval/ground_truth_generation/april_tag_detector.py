# import the necessary packages
import apriltag
import argparse
import glob
import cv2
import json
import numpy as np
import pandas as pd
import depthai as depthai


# def get_args():
# 	# Construct the Argument Parser and Parse the arguments.
#     arg_parser = argparse.ArgumentParser()
#     arg_parser.add_argument("-i", "--image", required=True,
# 	help="Path to input image containing AprilTag")
#     args = vars(arg_parser.parse_args())
#     return args


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
	pipeline = depthai.Pipeline()
    # Node for Camera data - 480p colour output.
	cam_rgb = pipeline.createColorCamera()
	cam_rgb.setPreviewSize(640, 480)
	cam_rgb.setInterleaved(False)
	cam_rgb.setFps(fps)
	# XLinkOut is a "way out" from the device. Any data you want to transfer to host need to be send via XLink
	xout_rgb = pipeline.createXLinkOut()
	xout_rgb.setStreamName("rgb")
	cam_rgb.preview.link(xout_rgb.input)
	return pipeline


def timeDeltaToMilliS(delta) -> float:
    return delta.total_seconds()*1000


def capture_save_images(pipeline, num_images_to_campture, output_dir_path):
	device = depthai.Device()
	with device:
		device.startPipeline(pipeline)
        # To consume the device results, we get one output queue from the device, with stream names we assigned earlier
		q_rgb = device.getOutputQueue("rgb")
		counter = 0
		cam_data = []
		while counter < num_images_to_campture:
            # We try to fetch the data from nn/rgb queues. tryGet will return either the data packet or None if there isn't any
			in_rgb = q_rgb.tryGet()
			if in_rgb is not None:
				device_timestamp = in_rgb.getTimestampDevice()
                # If the packet from RGB camera is present, we're retrieving the frame in OpenCV format using getCvFrame
				frame = in_rgb.getCvFrame()
				if frame is not None:
					counter += 1
					cv2.imshow("preview", frame)
					cv2.imwrite(f'{output_dir_path}/{counter}.png', frame)
					cam_data.append([timeDeltaToMilliS(device_timestamp), f"{counter}.png"])
            # At any time, you can press "q" and exit the main loop, therefore exiting the program itself
			if cv2.waitKey(1) == ord('q'):
				break
		cam_df = pd.DataFrame(cam_data, columns = ["#timestamp [ns]", "filename"])
		cam_df.to_csv(f'{output_dir_path}/data.csv', index=False)
		return cam_df
	

def process_images(images_for_processing):
	data_to_add_df = {
		'number_of_april_tags': [],
		'image_points': [],
		'successes': [],
		'rotation_vectors': [],
		'translation_vectors': []
	}
	for image_path in images_for_processing:
		# Load the input image and convert it to grayscale.
		print("[INFO] loading image...")
		image = cv2.imread(image_path)
		image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

		criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

		options = apriltag.DetectorOptions(families="tag36h11")
		detector = apriltag.Detector(options)
		results = detector.detect(image_gray)
		if len(results) > 0:
			# AprilTag detected!
			print("[INFO] {} total AprilTags detected".format(len(results)))

			world_pts = np.zeros((4, 3), np.float32)

			# We will only have at most one AprilTag per frame.
			result = results[0]

			# Extract the bounding box (x, y)-coordinates for the AprilTag
			# and convert each of the (x, y)-coordinate pairs to integers
			points = extract_bounding_boxes(result)
			print(result.corners)
			res = np.round(np.array(result.corners).reshape(4, 1, 2), 4)
			print(res)

			# points_refined = cv2.cornerSubPix(image_gray, res, (11, 11), (-1, -1), criteria)
			# print(points_refined)

			print(world_pts, world_pts.shape)
			
			(success, rotation_vector, translation_vector) = cv2.solvePnP(objectPoints=world_pts, imagePoints=res, cameraMatrix=camera_matrix, distCoeffs=distortion_coeff, flags=cv2.SOLVEPNP_P3P)

			print((success, rotation_vector, translation_vector))
			# WE ADD THESE RESULTS TO THE cam_df dataframe.

			for index in range(len(points)-1):
				cv2.line(image, points[index], points[index+1], (0, 255, 0), 2)

			# Draw the center (x, y)-coordinates of the AprilTag
			(cX, cY) = (int(result.center[0]), int(result.center[1]))
			cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)

			# Draw the tag family on the image
			tagFamily = result.tag_family.decode("utf-8")
			cv2.putText(image, tagFamily, (points[0][0], points[0][1] - 15),
				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
			print("[INFO] tag family: {}".format(tagFamily))
			break
		# Show the output image after AprilTag detection
		cv2.imshow("Image", image)
		cv2.waitKey(0)
	return data_to_add_df


if __name__ == "__main__":
	# args = get_args()

	# Load camera calibration data.
	calibration_filepath = "./Default_Calibration_Data/calib_18443010A177F50800.json"
	distortion_coeff, camera_matrix = load_camera_calibration_data(calibration_filepath)

	# Get color camera data.
	pipeline = create_pipeline(fps=1)

	# Connect to OAK-D and capture images.
	output_dir_path = './Ground_Truth_Images'
	cam_df = capture_save_images(pipeline=pipeline, num_images_to_campture=10, output_dir_path=output_dir_path)

	images_for_processing = glob.glob(f"{output_dir_path}/*.png")
	data_to_add_df = process_images(images_for_processing)

	# Add results(data_to_add_df) to cam_df!
	