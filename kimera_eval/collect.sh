#!/bin/bash

IP_ADDR=$1

# Run command on remote machine using ssh
ssh root@${IP_ADDR} 'bash -s' < run_kimera.sh
# Copy logs to host machine
scp "root@${IP_ADDR}:/home/root/output*.tar.gz" /home/sarika/indoor_drone_experimentation/kimera_eval/output_logs
# Cleanup logs on remote
ssh root@${IP_ADDR} 'rm -rf /home/root/output*.tar.gz'

./post_process.sh
