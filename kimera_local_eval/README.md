This directory contains a series of scripts and folders for various aspects of the main objective of getting Kimera-VIO working with a custom dataset:
* creating a custom dataset
* performing pose estimation with Kimera-VIO
* investigating pose estimates from Kimera-VIO 

Here is a brief explanation of the purpose of each directory.

There are many packages used across these folders. To avoid conflict with global pip packages, please create a virtual environment before installing packages specified in the requirements.txt file.

**Note**:
* The package pynput is used to track key presses and halt data capture. If using Wayland, keypresses are not detected in the library.


### Custom Datasets
* Custom datasets used for testing/experimenting with Kimera-VIO can be found here: (https://drive.google.com/file/d/1kJ_Z9BM6qG3DnuQ4b0NJyXqxIhUVbF4W/view?usp=drive_link).
* Ideally, these datasets should be located in the home directory under the following structure: /home/USERNAME/Datasets/[Contents of Zip file].
* The copy_dir_selection.sh script (found in scripts for dataset directory) should be placed in the Datasets directory and facilitates easy copy and pasting of datasets to be used for Kimera-VIO by placing the selected dataset into the mav0 directory.
* The directory, Kimera_VIO_Output, is where results from Kimera's execution are stored.


### Using the Docker Container
* The docker container is the easiest way one can use Kimera-VIO. You can follow the instructions on the MIT Kimera-VIO repository (https://github.com/MIT-SPARK/Kimera-VIO) to get setup. Note: When running the make commands ensure that they do not consume all CPU resources (use 'make -j 4' instead). Alternatively, you can use Shiva's docker container ().
* The following outlines the basic steps to execute a custom dataset with Kimera-VIO:
    - Setup docker container.
    - Copy necessary files over to container using the copy_necessary_files.sh script located in the directory scripts_for_docker_container.
    - In the datasets directory, run the copy_dir_selection.sh script - you will select a directory to be loaded into the mav0 directory. Kimera-VIO will load from this directory.
    - In the docker container, within the scripts directory, you will see two main scripts: execute_custom_dataset.sh and execute_euroc_dataset.sh. These scripts are named accordingly. Before executing, ensure that the correct dataset (custom/euroc) is loaded and you should specify a new directory for the results to be stored - this is done using the experiment_dir_name parameter within the scripts.
    - By default, ground truth is dsiabled. You would need to alter the EurocDataProvider.cpp file (uncomment line #458 and comment line #459) such that you enable the use of ground truth. This would be followed by a rebuild of the software.
    - In some instances, you need to prepend the call of either script with LIBGL_ALWAYS_SOFTWARE=1. This is necessary for 10th Gen Intel Chips.

### Directory Listing

* adding_error_euroc_dataset - This directory contains a series of scripts and notebooks dedicated towards introducing errors into the IMU and Camera timestamps respectively. Their primary purpose is to investigate the how much error is tolerable with Kimera-VIO's before experiencing degraded performance.

* BNO086_noise_analysis - This directory contains the results from obtaining noise and random walk parameters for the OAK-D. The experiments were executed for 1 hour with the OAK-D at test and Allan Variance Analysis was used for calcualtions. The 1 hour of data capture was not enough for accurate noise parameters. We opted to use nosie parameters from this post - https://qiita.com/nindanaoto/items/20858eca08aad90b5bab#calibrating-imu.

* calibration - This directory contains calibration parameters (at different resolutions) for the Euroc as well as our Custom Dataset. They are intended to be consumed by Kimera-VIO when testing.

* checking_jitter - This directory includes Python scripts and Jupyter Notebooks designed to collect data from accelerometer and gyroscope sensors. Focus is placed on investigating their timestamps for outliers, jitter, and testing bandwith of the connection between the OAK-D and the host (PC). 

* coordinate_frame_checks - This directory contains mainly notebooks dedicated towards visualising data captured from the OAK-D's accelerometer and gyroscope for the purposes of determining the corodinate frame of the OAK-D.

* delta_analysis - This directory contains Jupyter Notebooks used to investigate the timestamp deltas for our custom and Euroc datasets.

* ground_truth_generation - This directory is used for constructing groth truth pose which can be compared against Kimera-VIO pose estimates. The main script april_tag_detector.py detects AprilTags in images and computes the pose between the camera and the AprilTag (the script performs data capture and can also reference existing images).

* imu_timestamp_investigation - This directory contains a Jupyter notebook used for investigating the gyroscope and accelerometer timestamps on the OAK-D. From this we realised that we had to interpolate the sensor readings for the accelerometer since the acceleroemter and gyroscope were operating at different frequencies.

* kimera_data_generation - This directory contains scripts used for capturing data from the Luxonis OAK-D camera and preparing it into a format (like that of the Euroc dataset) that is easily consumed by Kimera-VIO.

* kimera_execution_analysis - This directory contains scripts used to analyse the output_logs directory from Kimera-VIO. It essentially provides insight into key information concerning the backend, frontend, etc. of Kimera-VIO when being ran on datasets.

* scripts_for_dataset_folder - This directory contains one script that is used to control which dataset is loaded for use with Kimera-VIO. It should be placed in the datasets directory.

* scripts_for_docker_container - This directory contains several bash scripts used to automate changes to parameters in Kimera-VIO and conduct experiments without the need for manual intervention.