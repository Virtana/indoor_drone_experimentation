import pandas as pd
import numpy as np

import os, sys

WRITE_FILES = bool(sys.argv[1])
MAX_JITTER = int(sys.argv[2])
WORKING_DIR = sys.argv[3]
CAMERA_TYPE= sys.argv[4]

def generate_error_normal_dist(mu, sigma):
    error = -1
    while error <0 or error > MAX_JITTER:
        error = np.random.normal(mu, sigma, 1)[0]
    return error


def generate_error_uniform_dist(lo, hi):
    return np.random.uniform(lo, hi, 1)


if __name__ == '__main__':
    # Load original csv.
    df = pd.read_csv(f'{WORKING_DIR}/mav0_euroc/{CAMERA_TYPE}/data.csv')
    df['#timestamp [ns]'] = df['#timestamp [ns]'].apply(lambda x: f"{x:.0f}")
    df['#timestamp [ns]'] = df['#timestamp [ns]'].astype('float64')

    # Check the deltas.
    orig_deltas = np.unique(np.diff(df['#timestamp [ns]']), return_counts=True)
    original_rate = 20
    reduction_factor = 1

    # Reducing frequency.
    df = df.iloc[::reduction_factor]

    # Check new deltas after downsampling.
    new_deltas = np.unique(np.diff(df['#timestamp [ns]']), return_counts=True)

    mu = MAX_JITTER * 0.5
    sigma = MAX_JITTER/4

    lo = -(MAX_JITTER/2)
    hi = (MAX_JITTER/2)

    default_ts_arr = df['#timestamp [ns]'].values.astype(int)
    steps = np.diff(default_ts_arr)
    adjusted_steps = []
    for step in steps:
        adjusted_steps.append(step + generate_error_uniform_dist(lo, hi))

    adjusted_steps = np.array(adjusted_steps)
    adjusted_steps = np.insert(adjusted_steps, 0, default_ts_arr[0], axis=0)
    modified_ts_arr = np.cumsum(adjusted_steps)
    df['#timestamp [ns]'] = modified_ts_arr
    df['#timestamp [ns]'] = df['#timestamp [ns]'].apply(lambda x: f"{x:.0f}")

    filename = f'data_modified_{MAX_JITTER / 1000000}ms_jitter.csv'

    if WRITE_FILES:
        df.to_csv(f'{WORKING_DIR}/mav0_euroc/{CAMERA_TYPE}/{filename}', index=False)
        os.system(f"cp {WORKING_DIR}/mav0_euroc/{CAMERA_TYPE}/{filename} {WORKING_DIR}/mav0/{CAMERA_TYPE}/{filename}")
        os.system(f"mv {WORKING_DIR}/mav0/{CAMERA_TYPE}/{filename} {WORKING_DIR}/mav0/{CAMERA_TYPE}/data.csv")

        mappings = {}

        for el in df.to_dict('records'):
            mappings[el['filename']] = el['#timestamp [ns]']
        
        for filename in os.listdir(f'{WORKING_DIR}/mav0/{CAMERA_TYPE}/data'):
            if filename in mappings.keys():
                os.rename(f'{WORKING_DIR}/mav0/{CAMERA_TYPE}/data/{filename}', f'{WORKING_DIR}/mav0/{CAMERA_TYPE}/data/{mappings[filename]}.png')