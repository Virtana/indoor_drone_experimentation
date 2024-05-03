#!/usr/bin/env python3

import matplotlib.pyplot as plt 
import math
import numpy as np
import pandas as pd
import sys

# Helper functions
def euclidean_dist(val1, val2) -> int:
    """
    val1 - [x,y,z] array for one point
    val2 - [x,y,z] array for other point
    """
    distance = np.linalg.norm(np.array(val1)-np.array(val2))
    return distance

gt_filepath=sys.argv[1]
vio_filepath=sys.argv[2]

print(f"gt file: {gt_filepath}; vio file: {vio_filepath}")

# Saving csv data to pandas objects
gt_df = pd.read_csv(gt_filepath)
vio_df = pd.read_csv(vio_filepath)

# Comparing x, y and z state estimates to ground truth over time.
plt.figure()
plt.subplot(3, 1, 1)
plt.plot(gt_df["#timestamp"], gt_df["x"])
plt.plot(vio_df["#timestamp"], vio_df["x"])
plt.legend(["gt", "vio"])
plt.title("x over time")

plt.grid()

plt.subplot(3, 1, 2)
plt.plot(gt_df["#timestamp"], gt_df["y"])
plt.plot(vio_df["#timestamp"], vio_df["y"])
plt.title("y over time")
plt.legend(["gt", "vio"])
plt.grid()

plt.subplot(3, 1, 3)
plt.plot(gt_df["#timestamp"], gt_df["z"])
plt.plot(vio_df["#timestamp"], vio_df["z"])
plt.title("z over time")
plt.legend(["gt", "vio"])
plt.grid()

plt.show()

# Comparing room ground truth vs state estimate

# ------------------------------------------------
# Comparing error over distance travelled
# ------------------------------------------------
# Getting start value
start_ts = vio_df['#timestamp'].iloc[0]
print(f"Start ts: {start_ts}")

# curr_index = gt_df["#timestamp"].index.searchsorted(start_ts)
curr_gt_index = gt_df[gt_df['#timestamp'] == start_ts].index[0]
print(f"Current gt index: {curr_gt_index}; value={gt_df.loc[curr_gt_index, ['x', 'y', 'z']].tolist()}")

# Starting value
last_gt_pos = gt_df.loc[curr_gt_index, ['x', 'y', 'z']].tolist()
total_dist = 0 # we get the total distance travelled up to that point

# Getting (x,y,z) value for each timestamp

# Iterating through the vio data frame
for ind in vio_df.index:
    vio_pos = vio_df.loc[ind, ['x', 'y', 'z']].tolist()
    gt_pos = gt_df.loc[curr_gt_index, ['x', 'y', 'z']].tolist()

    print(f"VIO (x,y,z): {vio_pos}")
    print(f"GT (x,y,z): {gt_pos}")

    print(f"State estimate error: {euclidean_dist(gt_pos, vio_pos)}")

    # Calculating overall distance travelled using ground truth
    # Euclidean distance travelled between last and current ground truth reading
    dist_travelled = euclidean_dist(last_gt_pos, gt_pos)
    total_dist = total_dist + abs(dist_travelled)
    print(f"Total distance travelled: {total_dist}")

    last_gt_pos = gt_pos
    # This timestamp matching approach is unfortunately too naive. 
    # Need to actually examine the timestamp values
    curr_gt_index += 4  

    # ---- possible approach to finding the next gt timestamp
    # initialise min_ts_diff to something large
    # Get next_vio_ts
    # increment gt_index. 
    # Get difference between next_gt_index and next_vio_ts
    # if ts_diff < min_ts_diff, then min_ts_diff = ts_diff
    # else 
    #     Assume we have found our closest time value. 
    #     Rationale: We will always start from a ts earlier than the vio ts.
    #     As we move towards it, the value will become smaller. A value after our
    #     ts that is smaller will still be closer. As we move later into the future,
    #     the difference will increase again. 
    #     When the diff is 0, this still holds. 


