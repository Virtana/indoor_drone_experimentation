import pandas as pd
import numpy as np

import os, sys

WRITE_FILES = bool(sys.argv[1])
MAX_JITTER = int(sys.argv[2])
WORKING_DIR = sys.argv[3]

def generate_error(mu, sigma):
    error = -1
    while error <0 or error > MAX_JITTER:
        error = np.random.normal(mu, sigma, 1)[0]
    return error


if __name__ == '__main__':
    working_dir = '/home/shiva/Datasets/V2_01_easy/V2_01_easy'

    df = pd.read_csv(working_dir + '/mav0_euroc/imu0/data.csv')
    df['#timestamp [ns]'] = df['#timestamp [ns]'].apply(lambda x: f"{x:.0f}")
    df['#timestamp [ns]'] = df['#timestamp [ns]'].astype('float64')

    # Check the deltas.
    orig_deltas = np.unique(np.diff(df['#timestamp [ns]']), return_counts=True)
    original_rate = 200
    reduction_factor = 1

    # Reducing frequency
    df = df.iloc[::reduction_factor]

    # Check deltas after downsampling.
    new_deltas = np.unique(np.diff(df['#timestamp [ns]']), return_counts=True)

    mu = MAX_JITTER * 0.5
    sigma = MAX_JITTER/4

    default_ts_arr = df['#timestamp [ns]'].values.astype(int)

    steps = np.diff(default_ts_arr)
    adjusted_steps = []
    for step in steps:
        adjusted_steps.append(step + generate_error(mu, sigma))

    adjusted_steps = np.array(adjusted_steps)
    adjusted_steps = np.insert(adjusted_steps, 0, default_ts_arr[0], axis=0)
    modified_ts_arr = np.cumsum(adjusted_steps)
    df['#timestamp [ns]'] = modified_ts_arr
    df['#timestamp [ns]'] = df['#timestamp [ns]'].apply(lambda x: f"{x:.0f}")
    
    if WRITE_FILES:
        filename = f'data_modified_{MAX_JITTER / 1000000}ms_jitter.csv'
        df.to_csv(working_dir + f'/mav0_euroc/imu0/{filename}', index=False)
        os.system(f"cp {working_dir}/mav0_euroc/imu0/{filename} {working_dir}/mav0/imu0/{filename}")
        os.system(f"mv {working_dir}/mav0/imu0/{filename} {working_dir}/mav0/imu0/data.csv")

