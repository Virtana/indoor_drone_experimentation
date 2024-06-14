# Kimera Evaluation

This directory contains scripts that are used to evaluated Kimera-VIO's performance in terms of:

1. Accuracy i.e. how much error is there over time?
2. How fast the Kimera application can run with different VIO configurations.

Only EuRoC datasets are considered. These can be downloaded from [here](https://projects.asl.ethz.ch/datasets/doku.php?id=kmavvisualinertialdatasets)

## Assessing Error over time
`drift_assessment.py` takes the directory with the Kimera-VIO output logs as input and takes `traj_gt.csv` and `traj_vio.csv` to do the following:
1. Display the variation between x, y and z state estimates and ground truth over time (`gtvio_xyz.png`).
2. Show how the percentage error changes with distance (`errpercent_dist.png`).
3. Shows the error value over time (`errvsdist.png`).

Dependencies should be installed in a virtual environment as follows:
```
python3 -m venv venv
pip install -r requirements.txt
```

To run this script as a standalone:
```
python drift_assessment.py </path/to/output_logs>
```
The output CSV files and graphs will be saved to the _same_ input log directory.

## Kimera Test Automation
This is carried out by 3 bash scripts:
1. `collect.sh` - This is the main script that executes all other 
2. `run_kimera.sh` - This is run on the SoM over SSH by `collect.sh`. It is responsible for reconfiguring the Kimera-VIO frontend and backend and the associated bash script which runs Kimera. 
3. `post_process.sh` - This is run on the host machine by `collect.sh` and is responsible for un-tarring files and running `drift_assessment.py` on the extracted logs. 

The `tar.gz` files are copied from the SoM to the `output_logs` directory and the extracted and processed logs can be found in `extracted_logs`.

### Setup for using `collect.sh`
`run_kimera.sh` assumes the following:
1. The Kimera-VIO repository can be found at `/home/root/Kimera-VIO` on the SoM and that build files are in `/home/root/Kimera-VIO/build`
2. All of your datasets are in `/home/root`
3. That the EuRoC datasets have already been yamelized. This can be done as follows:
```
cd ~/Kimera-VIO/scripts/euroc/
bash yamelize.bash -p PATH_TO_YOUR_EUROC_DATASET
```
4. The datasets can be set in the `DATASETS` variable. We assume the following are used: "V1_01_easy", "V2_01_easy", "V1_02_medium".

To run `collect.sh`, you will need to specify your SoM's IP address. To get this, run `ifconfig` when connected to the SoM over serial. 

```
cd /path/to/indoor_drone_experimentation/kimera_eval
./collect.sh <IP Address>
```