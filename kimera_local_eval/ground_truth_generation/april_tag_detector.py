# import the necessary packages
import apriltag
import argparse
import cv2


def get_args():
	# Construct the Argument Parser and Parse the arguments.
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-i", "--image", required=True,
	help="Path to input image containing AprilTag")
    args = vars(arg_parser.parse_args())
    return args


def extract_bounding_boxes(result):
	(ptA, ptB, ptC, ptD) = result.corners
	ptB = (int(ptB[0]), int(ptB[1]))
	ptC = (int(ptC[0]), int(ptC[1]))
	ptD = (int(ptD[0]), int(ptD[1]))
	ptA = (int(ptA[0]), int(ptA[1]))
	return (ptA, ptB, ptC, ptD)


if __name__ == "__main__":
	args = get_args()

    # Load the input image and convert it to grayscale.
	print("[INFO] loading image...")
	image = cv2.imread(args["image"])
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Define the AprilTags detector options and then detect the AprilTags
    # In the input image
	print("[INFO] detecting AprilTags...")
	options = apriltag.DetectorOptions(families="tag36h11")
	detector = apriltag.Detector(options)
	results = detector.detect(gray)
	print("[INFO] {} total AprilTags detected".format(len(results)))

    # Loop over the AprilTag detection results
	for result in results:
        # Extract the bounding box (x, y)-coordinates for the AprilTag
        # and convert each of the (x, y)-coordinate pairs to integers
		points = extract_bounding_boxes(result)

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
    # Show the output image after AprilTag detection
	cv2.imshow("Image", image)
	cv2.waitKey(0)