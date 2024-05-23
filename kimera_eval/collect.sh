#!/bin/bash

# Run command on remote machine using ssh
ssh root@192.168.100.243 'bash -s' < run_kimera.sh
# Copy logs to host machine
scp 'root@192.168.100.243:/home/root/output*.tar.gz' /home/sarika/indoor_drone_experimentation/kimera_eval/output_logs
# Cleanup logs on remote
ssh root@192.168.100.243 'rm -rf /home/root/output*.tar.gz'
