This directory contains a series of scripts and folders for various aspects of the main objective of
creating a custom dataset, performing pose estimation with Kimera-VIO and validating the results. 
Here is a brief explanation of the purpose of each directory.

There are many packages used across these folders. To avoid conflict with global pip packages, please create a virtual
environment before installing packages specified in the requirements.txt file.

### Directory Listing


* adding_error_euroc_dataset - This directory contains a series of scripts and notebooks dedicated towards introducing errors into the IMU and Camera timestamps respectively. Their primary purpose is to investigate the how much error is tolerable with Kimera-VIO's before experiencing degraded performance.

* calibration - This directory contains calibration parameters (at different resolutions) for the Euroc as well as our Custom Dataset. They are intended to be consumed by Kimera-VIO when testing.

* checking_jitter - This directory includes Python scripts and Jupyter Notebooks designed to collect data from accelerometer and gyroscope sensors. Focus is placed on investigating their timestamps for outliers, jitter, and testing bandwith of the connection between the OAK-D and the host (PC). 

* coordinate_frame_checks - This directory contains mainly notebooks dedicated towards visualising data captured from the OAK-D's accelerometer and gyroscope for the purposes of determining the corodinate frame of the OAK-D.

* delta_analysis - This directory contains Jupyter Notebooks used to investigate the timestamp deltas for our custom and Euroc datasets.

* ground_truth_generation - This directory is used for constructing groth truth pose which can be compared against Kimera-VIO pose estimates. The main script april_tag_detector.py detects AprilTags in images and computes the pose between the camera and the AprilTag (the script performs data capture and can also reference existing images).

* kimera_data_generation - This directory contains scripts used for capturing data from the Luxonis OAK-D camera and preparing it into a format (like that of the Euroc dataset) that is easily consumed by Kimera-VIO.

* kimera_execution_analysis - This directory contains scripts used to analyse the output_logs directory from Kimera-VIO. It essentially provides insight into key information concerning the backend, frontend, etc. of Kimera-VIO when being ran on datasets.

* scripts_for_docker_container - This directory contains several bash scripts used to automate changes to parameters in Kimera-VIO and conduct experiments without the need for manual intervention.