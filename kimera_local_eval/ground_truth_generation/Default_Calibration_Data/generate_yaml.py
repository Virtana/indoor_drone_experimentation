import json
import yaml

import numpy as np


def determine_scaling_factor(camera_calibration_resolution, image_size):
	height_scale = image_size[1]/camera_calibration_resolution[0]
	width_scale = image_size[0]/camera_calibration_resolution[1]
	print(camera_calibration_resolution)
	print(image_size)
	return (height_scale, width_scale)


def extract_adjust_camera_calibration(camera_calibration, image_size):
    camera_calibration_resolution = (camera_calibration['height'], camera_calibration['width'])
    height_scaling_factor, width_scaling_factor = determine_scaling_factor(camera_calibration_resolution, image_size)
    print(f"Scaling factor applied: H: {height_scaling_factor}, W: {width_scaling_factor}")
    distortion_coeff = np.array(camera_calibration['distortionCoeff'])
    intrinsic_matrix = np.array(camera_calibration['intrinsicMatrix'])
    rotation_matrix = np.array(camera_calibration['extrinsics']['rotationMatrix'])
    # Kimera-VIO expects distances in meters. We also adjust the x and y translation values based on the respective scaling factors.
    translation_matrix = np.array(list(camera_calibration['extrinsics']['translation'].values())).reshape(3,1) / 100
    # translation_matrix[0] *= width_scaling_factor
    # translation_matrix[1] *= height_scaling_factor
    params_dict = {}
    params_dict['camera_id'] = 'left_cam'
    params_dict['T_BS'] = {
        'cols': 4,
        'rows': 4,
        'data': np.vstack((np.hstack((rotation_matrix, translation_matrix)), np.array([0.0, 0.0, 0.0, 1.0]))).tolist()
    }
    params_dict['rate_hz'] = 4
    params_dict['resolution'] = [image_size[0], image_size[1]]
    params_dict['camera_model']='pinhole'
    params_dict['intrinsics']= [float(intrinsic_matrix[0][0]) * width_scaling_factor, 
                                float(intrinsic_matrix[1][1]) * height_scaling_factor,
                                float(intrinsic_matrix[0][2]) * width_scaling_factor, 
                                float(intrinsic_matrix[1][2]) * height_scaling_factor]
    params_dict['distortion_model'] ='radial-tangential'
    params_dict['distortion_coefficients']= [float(distortion_coeff[0]), float(distortion_coeff[1]), float(distortion_coeff[2]), float(distortion_coeff[3])]
    return params_dict


if __name__ == "__main__":
    calibration_file = 'calib_18443010A177F50800.json'
    # Width is the first value and height is the second.
    image_size = (1280, 800)
    with open(calibration_file, 'r') as file:
        data = json.load(file)

	# # The data object is an array representing the three cameras as well as IMU on the OAK-D.
	# # The mono cameras are identified by indicies 0(right) and 1(left); and the color camera is identified by index 2.
    if data is not None:
        left_camera_calibration = extract_adjust_camera_calibration(data['cameraData'][1][1], image_size)
        right_camera_calibration = extract_adjust_camera_calibration(data['cameraData'][0][1], image_size)
        
        # print("Left Cam Calibration:", left_camera_calibration)
        with open('LeftCameraParams_V2.yaml', 'w') as output_file:
            yaml.dump(left_camera_calibration, output_file, default_flow_style=None)

        print("\n\n\n")
        # print("Right Cam Calibration:", right_camera_calibration)
        with open('RightCameraParams_V2.yaml', 'w') as output_file:
            yaml.dump(right_camera_calibration, output_file, default_flow_style=None)
    else:
        exit(1)
