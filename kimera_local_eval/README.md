This directory contains a series of scripts and folders for various aspects of the main objective of
creating a custom dataset, performing pose estimation with Kimera-VIO and validating the results. Here is a brief explanation of the purpose of each directory.

There are many packages used across these folders. To avoid conflict with global pip packages, please create a virtual
environment before installing packages specified in the requirements.txt file.

### Unordered

* Checking Jitter - This directory includes Python scripts and Jupyter Notebooks designed to collect data from accelerometer and gyroscope sensors, as well as to plot the differences between data points to analyze the jitter from these sensors.
* Delta Analysis - This directory contains Jupyter Notebooks used to investigate the deltas for datasets (namely our custom datasets as well as the Euroc dataset).
* Euroc Dataset Corruption - This directory contains Jupyter notebooks which can remove data points and/or add jitter to the Euroc dataset. This is primarily used for testing robustness.
* Ground Truth Generation - This directory is used for constructing groth truth pose which can be compared against Kimera-VIO pose estimates. The main script april_tag_detector.py detects AprilTags in images and computes the pose between the camera and the AprilTag (the script performs data capture and can also reference existing images).
* Kimera Data Generation - This directory contains scripts used for capturing data from the Luxonis OAK-D camera and preparing it into a format (like that of the Euroc dataset) that is easily processed by Kimera-VIO.
* Kimera Execution Analysis - This directory contains scripts used to analyse the output_logs directory from Kimera-VIO. It essentially provides insight into key information concerning the backend, frontend, etc. of Kimera-VIO when being ran on datasets.
* Pose Evaluation - This directory contaiins folders, each of which pertain to the evaluation of the pose estimates produced by Kimera-VIO acorss multiple datasets. The root directory contains a skeletion notebook which can then be copied into a new folder to perform analysis.
* Scripts for Docker Container - This directory contains bash scripts used to quick copy/paste of files/folders to and from the Kimera-VIO docker container.