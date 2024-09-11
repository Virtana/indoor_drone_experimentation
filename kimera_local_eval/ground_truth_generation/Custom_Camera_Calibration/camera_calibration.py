import argparse
import cv2
import os
import shutil
import glob
import pickle
import numpy as np
import depthai as dai


def create_pipeline():
    # Start defining a pipeline
    pipeline = dai.Pipeline()
    # Define a source - color camera
    cam = pipeline.create(dai.node.ColorCamera)
    # Script node
    script = pipeline.create(dai.node.Script)
    script.setScript("""
        import time
        ctrl = CameraControl()
        ctrl.setCaptureStill(True)
        while True:
            time.sleep(1)
            node.io['out'].send(ctrl)
    """)
    # XLinkOut
    xout = pipeline.create(dai.node.XLinkOut)
    xout.setStreamName('still')
    # Connections
    script.outputs['out'].link(cam.inputControl)
    cam.still.link(xout.input)
    return pipeline


def capture_calibration_images(output_dir, capture_limit):
    pipeline = create_pipeline()
    # Connect to device with pipeline
    with dai.Device(pipeline) as device:
        counter = 0
        while counter < capture_limit:
            img = device.getOutputQueue("still").get()
            cv2.imshow('still', img.getCvFrame())
            cv2.imwrite(f'{output_dir}{counter}.png', img.getCvFrame())
            if cv2.waitKey(1) == ord('q'):
                break
            counter += 1


def setup_output_directory(output_dir_path, wipe_dir):
    if os.path.exists(output_dir_path):
        if wipe_dir:
            shutil.rmtree(output_dir_path)
            os.makedirs(output_dir_path)
            return True
        else:
            return False
    else:
        os.makedirs(output_dir_path)
        return True
    

def get_2d_3d_points(output_dir, chessboard_size):
    # Termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # Prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
    objp[:,:2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1,2)
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d Points in real world space.
    imgpoints = [] # 2d Points in image plane.
    images = glob.glob(f"{output_dir}*.png")
    for fname in images:
        image = cv2.imread(fname)
        gray_color_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray_color_image, (chessboard_size[0], chessboard_size[1]), None)
        print("CORNERS!!!!!")
        print(type(corners))
        print(corners.size)
        print(corners.shape)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            corners2 = cv2.cornerSubPix(gray_color_image, corners, (11, 11), (-1,-1), criteria)
            print(corners2)
            imgpoints.append(corners2)
            # Draw and display the corners
            cv2.drawChessboardCorners(image, (chessboard_size[0], chessboard_size[1]), corners2, ret)
            cv2.imshow('img', image)
            cv2.waitKey(500)
    cv2.destroyAllWindows()
    return objpoints, imgpoints, gray_color_image


def get_args():
	# Construct the Argument Parser and Parse the arguments.
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-ni", "--number_of_calibration_images", required=True, help="Number of calibration images to capture")
    arg_parser.add_argument("-nr", "--number_of_rows", required=True, help="Number of rows on chessboard")
    arg_parser.add_argument("-nc", "--number_of_cols", required=True, help="Number of columns in chessboard")
    args = vars(arg_parser.parse_args())
    return args


def save_pkl(filename, data):
    with open(filename, "wb") as file_handler:
        pickle.dump(data, file_handler)
        file_handler.close()


if __name__ == "__main__":
    args = get_args()

    image_output_dir = "./Calibration_Images/"
    calibration_output_dir = "./Calibration_Data/"

    num_calibration_images = int(args['number_of_calibration_images'])
    if num_calibration_images != 0:
        print("Capturing new images for calibration.")
        if setup_output_directory(image_output_dir, True):
            capture_calibration_images(image_output_dir, num_calibration_images)
        else:
            print("Error setting up calibration image directory.")
            print("Program will now exit.")
            exit()
    else:
        print("Skpping image capture, calibrating based on existing data.")
    
    if not(setup_output_directory(calibration_output_dir, True)):
            print("Error setting up calibration data directory.")
            print("Program will now exit.")
            exit()
    
    chessboard_size = (int(args["number_of_rows"]), int(args["number_of_cols"]))
    objpoints, imgpoints, gray_color_image = get_2d_3d_points(image_output_dir, chessboard_size)

    # Perform camera calibration by 
    # passing the value of above found out 3D points
    # and its corresponding pixel coordinates of the 
    # detected corners (2D points). 
    ret, matrix, distortion, r_vecs, t_vecs = cv2.calibrateCamera(objpoints, imgpoints, gray_color_image.shape[::-1], None, None) 

    # Displaying required output 
    print(" Camera matrix:") 
    print(matrix)
    save_pkl('./Calibration_Data/camera_matrix.pkl', matrix)
    
    print("\n Distortion coefficient:") 
    print(distortion)
    save_pkl('./Calibration_Data/camera_distortion.pkl', distortion)
    
    print("\n Rotation Vectors:") 
    print(r_vecs)
    save_pkl('./Calibration_Data/r_vec.pkl', r_vecs)
    
    print("\n Translation Vectors:") 
    print(t_vecs)
    print("Program will now exit.")
    save_pkl('./Calibration_Data/t_vec.pkl', t_vecs)