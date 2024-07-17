#!/bin/bash

dir="extracted_logs"
log_dirs=($(find "$dir" -mindepth 1 -maxdepth 1 -type d))
for dir in "${log_dirs[@]}"; do
    python drift_assessment.py ${dir}
done