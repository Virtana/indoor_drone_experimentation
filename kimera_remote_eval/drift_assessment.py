#!/usr/bin/env python3

import matplotlib.pyplot as plt 
import numpy as np
import os
import pandas as pd
import sys

DEBUG = False

# Helper functions
def euclidean_dist(val1, val2) -> int:
    """
    val1 - [x,y,z] array for one point
    val2 - [x,y,z] array for other point
    """
    distance = np.linalg.norm(np.array(val1)-np.array(val2))
    return distance

def match_gt_vio_ts(gt_df, vio_df, start_gt_index, vio_index) -> int:
    # ------------------------------------------------------------------------
    # Getting the corresponding gt_ts/index for the next iteration of the loop
    # ------------------------------------------------------------------------
    # Initialise min_ts_diff to something arbitrarily large
    min_ts_diff = 1000000000000000000
    # Get corresponding vio_ts
    vio_ts = vio_df['#timestamp'].iloc[vio_index]
    
    # We increment the ground truth index until we find the smallest difference between the
    # vio ts and the gt ts
    next_gt_ind = start_gt_index + 1
    ts_diff = abs(vio_ts - gt_df['#timestamp'].iloc[next_gt_ind])
    min_ts_index = 0

    #     Rationale: We will always start from a ts earlier than the vio ts.
    #     As we move towards it, the value will become smaller. A value after our
    #     ts that is smaller will still be closer. As we move later into the future,
    #     the difference will increase again. 
    #     When the diff is 0, this still holds.
    num_gt_indices = len(gt_df.index)-1
    while ts_diff < min_ts_diff and next_gt_ind < num_gt_indices:
        min_ts_diff = ts_diff 
        min_ts_index = next_gt_ind

        # Updating ts_diff for the next iteration
        next_gt_ind += 1
        ts_diff = abs(vio_ts - gt_df['#timestamp'].iloc[next_gt_ind])

    if DEBUG:
        print(f"Min ts_diff: {min_ts_diff}")
    return min_ts_index # Updating curr_gt_index for the next iteration

gt_filepath = os.path.join(sys.argv[1], "traj_gt.csv")
vio_filepath = os.path.join(sys.argv[1], "traj_vio.csv")

print(f"gt file: {gt_filepath}; vio file: {vio_filepath}")

# Saving csv data to pandas objects
gt_df = pd.read_csv(gt_filepath)
vio_df = pd.read_csv(vio_filepath)

# -----------------------------------------------------------------
# Comparing x, y and z state estimates to ground truth over time.
# -----------------------------------------------------------------
# Generating time passed using timestamp data
# For ground truth
gt_time_passed = []
total_time = 0
for i in range(len(gt_df)):
    if i == 0:
        gt_time_passed.append(0)
    else:
        time_diff_ms = (gt_df['#timestamp'].iloc[i] - gt_df['#timestamp'].iloc[i-1])/1000000
        total_time += time_diff_ms
        gt_time_passed.append(total_time)    

gt_time_ms_df = pd.DataFrame(gt_time_passed, columns=['time_ms'])

# For VIO state estimate
# Finding the offset between ground truth and vio estimates
gt_vio_start_diff = (vio_df['#timestamp'].iloc[0] - gt_df['#timestamp'].iloc[0])/1000000

vio_time_passed = []
total_time = gt_vio_start_diff
for i in range(len(vio_df)):
    if i == 0:
        vio_time_passed.append(0)
    else:
        time_diff_ms = (vio_df['#timestamp'].iloc[i] - vio_df['#timestamp'].iloc[i-1])/1000000
        total_time += time_diff_ms
        vio_time_passed.append(total_time)
vio_time_ms_df = pd.DataFrame(vio_time_passed, columns=['time_ms'])

plt.figure()
plt.subplot(3, 1, 1)
plt.plot(gt_time_ms_df["time_ms"], gt_df["x"])
plt.plot(vio_time_ms_df["time_ms"], vio_df["x"])
plt.legend(["gt", "vio"])
plt.xlabel("time/ms")
plt.ylabel("x position/m")
plt.title("x over time")
plt.grid(True, which='both', linestyle='--')
plt.minorticks_on()

plt.subplot(3, 1, 2)
plt.plot(gt_time_ms_df["time_ms"], gt_df["y"])
plt.plot(vio_time_ms_df["time_ms"], vio_df["y"])
plt.title("y over time")
plt.xlabel("time/ms")
plt.ylabel("y position/m")
plt.legend(["gt", "vio"])
plt.grid(True, which='both', linestyle='--')
plt.minorticks_on()

plt.subplot(3, 1, 3)
plt.plot(gt_time_ms_df["time_ms"], gt_df["z"])
plt.plot(vio_time_ms_df["time_ms"], vio_df["z"])
plt.title("z over time")
plt.legend(["gt", "vio"])
plt.xlabel("time/ms")
plt.ylabel("z position/m")
plt.grid(True, which='both', linestyle='--')
plt.minorticks_on()

plt.tight_layout()
plt.savefig(os.path.join(sys.argv[1], "gtvio_xyz.png"))
# ------------------------------------------------
# Comparing error over distance travelled
# ------------------------------------------------
# Getting starting timestamp for state updates
start_ts = vio_df['#timestamp'].iloc[0]

if DEBUG:
    print(f"Start ts: {start_ts}")

# Finding the corresponding ground truth timestamp and position at which to start
curr_gt_index = match_gt_vio_ts(gt_df, vio_df, 0, 0)

# Starting value
last_gt_pos = gt_df.loc[curr_gt_index, ['x', 'y', 'z']].tolist()

# Generating an array with the total distance travelled up to every single point from our "start" value
# We will be comparing the error against the total distance travelled (rather than displacement).
total_dist = 0 # we get the total distance travelled up to that point

dist_update = [] # empty list to which values will be added
for i in range(curr_gt_index, len(gt_df)-1):
    last_pos = [0,0,0]
    if i == curr_gt_index:
        last_pos = last_gt_pos
    else:
        last_pos = gt_df.loc[i-1, ['x', 'y', 'z']].tolist()
    
    current_pos = gt_df.loc[i, ['x', 'y', 'z']].tolist()
    dist_moved = abs(euclidean_dist(current_pos, last_pos))

    total_dist = total_dist + dist_moved

    data = [i, total_dist]
    dist_update.append(data)

dist_travelled_df = pd.DataFrame(dist_update, columns=['gt_index', 'distance'])
dist_travelled_df.to_csv(os.path.join(sys.argv[1],"distance_travelled.csv"))

# -------------
# Iterating through the vio data frame

error_calcs = [] # empty list to which values will be added
num_vio_ind=len(vio_df.index)

for ind in vio_df.index:
    # For our current vio 
    curr_vio_ts = vio_df['#timestamp'].iloc[ind]
    curr_vio_pos = vio_df.loc[ind, ['x', 'y', 'z']].tolist()

    if DEBUG:
        print(f"Current gt index: {curr_gt_index}; value={gt_df.loc[curr_gt_index, ['x', 'y', 'z']].tolist()}")
        print(f"vio ts: {curr_vio_ts}; pos: {curr_vio_pos}")

    # Ground truth info for corresponding ts (calculated on previous iteration)
    gt_pos = gt_df.loc[curr_gt_index, ['x', 'y', 'z']].tolist()

    if DEBUG:
        print(f"State estimate error: {euclidean_dist(gt_pos, curr_vio_pos)}")

    estimate_error = euclidean_dist(gt_pos, curr_vio_pos)
    x_err = curr_vio_pos[0] - gt_pos[0]
    y_err = curr_vio_pos[1] - gt_pos[1]
    z_err = curr_vio_pos[2] - gt_pos[2]

    # Getting distance travelled up this this point in the trajectory
    try:
        dist_index = dist_travelled_df[dist_travelled_df['gt_index'] == curr_gt_index].index[0]
        distance = dist_travelled_df.loc[dist_index, 'distance']
    except Exception as e:
        print(f"exception raised, so breaking out of loop: {e}")
        print(dist_travelled_df[dist_travelled_df['gt_index'] == curr_gt_index])
        break   #exit loop, since we are probably out of range

    if abs(distance) < 0.001:
        percent_err = 0
    else:
        percent_err = (estimate_error/distance)*100
    data = [curr_vio_ts, gt_pos, curr_vio_pos, distance, estimate_error, percent_err, x_err, y_err, z_err]
    error_calcs.append(data)

    # Getting the corresponding gt_ts/index for the next iteration of the loop
    if (ind+1) > num_vio_ind: # No next value
        print(f"Exiting loop because next vio index i: {ind+1}")
        break

    curr_gt_index=match_gt_vio_ts(gt_df, vio_df, start_gt_index=curr_gt_index, vio_index=ind+1)
    
error_df = pd.DataFrame(error_calcs, columns=['vio_ts', 'gt_pos', 'vio_pos', 'distance', 'error', 'percent_err', 'x_err', 'y_err', 'z_err'])
error_df.to_csv(os.path.join(sys.argv[1],"drift_error.csv"))

plt.figure()
plt.plot(error_df["distance"], error_df["percent_err"])
plt.xlabel("Distance travelled (m)")
plt.ylabel("% Error")
plt.title("% Error as distance travelled increases")
plt.grid(True, which='both', linestyle='--')
plt.minorticks_on()
plt.savefig(os.path.join(sys.argv[1], "errpercent_dist.png"))

plt.figure()
plt.plot(error_df["distance"], error_df["error"])
plt.xlabel("Distance travelled (m)")
plt.ylabel("Error (m)")
plt.title("Error as distance travelled increases")
plt.grid(True, which='both', linestyle='--')
plt.minorticks_on()
plt.savefig(os.path.join(sys.argv[1], "errvsdist.png"))

# -----------------------------------------------------------------
# Comparing x, y and z individual error change over distance.
# -----------------------------------------------------------------
plt.figure()
plt.subplot(3, 1, 1)
plt.plot(error_df["distance"], error_df["x_err"])
plt.ylabel("x error (m)")
plt.title("x error over distance")
plt.grid(True, which='both', linestyle='--')
plt.minorticks_on()

plt.subplot(3, 1, 2)
plt.plot(error_df["distance"], error_df["y_err"])
plt.ylabel("y error (m)")
plt.title("y error over distance")
plt.grid(True, which='both', linestyle='--')
plt.minorticks_on()

plt.subplot(3, 1, 3)
plt.plot(error_df["distance"], error_df["z_err"])
plt.xlabel("distance travelled (m)")
plt.ylabel("z error (m)")
plt.title("z error over distance")
plt.grid(True, which='both', linestyle='--')
plt.minorticks_on()

plt.tight_layout()
plt.savefig(os.path.join(sys.argv[1], "xyz_errs_distance.png"))

# -----------------------------------------------------------------
# Comparing x, y and z individual error change over time.
# -----------------------------------------------------------------
plt.figure()
plt.subplot(3, 1, 1)
plt.plot(vio_time_ms_df['time_ms'][:len(error_df)], error_df["x_err"])
plt.ylabel("x error (m)")
plt.xlabel("time/ms")
plt.title("x error with time")
plt.grid(True, which='both', linestyle='--')
plt.minorticks_on()

plt.subplot(3, 1, 2)
plt.plot(vio_time_ms_df['time_ms'][:len(error_df)], error_df["y_err"])
plt.ylabel("y error (m)")
plt.xlabel("time/ms")
plt.title("y error with time")
plt.grid(True, which='both', linestyle='--')
plt.minorticks_on()

plt.subplot(3, 1, 3)
plt.plot(vio_time_ms_df['time_ms'][:len(error_df)], error_df["z_err"])
plt.xlabel("time/ms")
plt.ylabel("z error (m)")
plt.title("z error with time")
plt.grid(True, which='both', linestyle='--')
plt.minorticks_on()

plt.tight_layout()
plt.savefig(os.path.join(sys.argv[1], "xyz_errs_time.png"))
if DEBUG:
    plt.show()
