#!/bin/bash

# Directory to search for .tar.gz files
search_dir="output_logs"

# Find all .tar.gz files and store them in an array
files=($(find "$search_dir" -maxdepth 1 -type f -name "*.tar.gz"))

# Check if any .tar.gz files are found
if [ ${#files[@]} -eq 0 ]; then
    echo "No .tar.gz files found in $search_dir"
else
    echo "Found ${#files[@]} .tar.gz files:"
    # Print all the files in the array
    for file in "${files[@]}"; do
        tar -xvf ${file} -C extracted_logs
    done
    mv extracted_logs/home/root/* extracted_logs
    rm -rf extracted_logs/home/

    dir="extracted_logs"
    log_dirs=($(find "$dir" -mindepth 1 -maxdepth 1 -type d))
    for dir in "${log_dirs[@]}"; do
        python drift_assessment.py ${dir}
    done
fi

# Move all processed tar.gz files into a subfolder so that they won't be reprocessed
date=`date | sed 's/ /_/g'`
cleanup_dir="${search_dir}/output_${date}"
mkdir ${cleanup_dir}
mv ${search_dir}/*.tar.gz ${cleanup_dir}
