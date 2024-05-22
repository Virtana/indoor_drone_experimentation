#!/bin/bash

# Run command on remote machine using ssh
# ssh root@MachineB 'bash -s' < local_script.sh
ssh root@192.168.100.243 'bash -s' < run_kimera.sh

scp 'root@192.168.100.243:/home/root/output*.tar.gz' /home/sarika/indoor_drone_experimentation/kimera_eval/output_logs