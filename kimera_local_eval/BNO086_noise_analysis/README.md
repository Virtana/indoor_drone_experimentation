# Instructions

1. Have ROS installed (I used the setup from Kimera-VIO-ROS which sets up a Docker container).
2. Capture data on the OAK-D for 1-2 hours using the data_capture_imu_only.py script (located in the kimera_data_generation directory). There is already existing data (capttured for 1 hour) - https://drive.google.com/file/d/1auwC_vvur5pHm0q-MTiwNhjp2P5zwcA6/view?usp=drive_link. 
3. Create a Bag file using the data by using the Python script - create_rosbag.py.
4. Create a new catkin workspace and ensure that it is activated.
5. Install the code_utils package (https://github.com/gaowenliang/code_utils) by firstly cloning the repo and running catkin_make. 
6. Then install the imu_utils package (https://github.com/gaowenliang/imu_utils) by firstly cloning the repo and running catkin_make. Note: If you attempt to install both packages at the same time, you will encounter errors.
7. The following file changes also need to be made:
    * Change the following references across all files:
        * CV_LOAD_IMG_UNCHANGED to cv::IMREAD_UNCHANGED
        * CV_MINMAX to cv::NORM_MINMAX
    * Change #include "backward.hpp" to #include "/code_utils/backward.hpp" in the following files:
        * sumpixel_test.cpp
        * mat_test_io.pp
8. Within the Docker container, ensure that the Bag and imu.launch files are copied over.
9. Run the following commands:
    * roscore
    * roslaunch imu.launch
    * rosbag play -r 200 NAME_OF_BAG_FILE
    <br>
   You should see .yaml and .txt files output in the output directory (specified in imu.launch - by default it's the container's root directory)).