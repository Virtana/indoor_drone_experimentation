# Kimera Evaluation

This directory contains scripts that are used to evaluated Kimera-VIO's performance in terms of:

1. Accuracy i.e. how much error is there over time?
2. How fast the Kimera application can run - Not implemented yet.

`drift_assessment.py` takes the directory with the Kimera-VIO output logs as input and takes `traj_gt.csv` and `traj_vio.csv` to do the following:
1. Display the variation between x, y and z state estimates and ground truth over time.
2. Show how the percentage error changes with distance. 