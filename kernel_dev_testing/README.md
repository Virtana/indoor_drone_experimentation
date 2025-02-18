# Indoor Drone Experimentation - Linux Kernel

## Building the Linux Kernel
1. Build the docker container using the `build_container.sh` script.
2. Run the docker container using the `run_container.sh` script.
3. Apply the kernel config: `make ${MACHINE}_defconfig compulab.config modified.config O=../build/`
4. Build the kernel: ```make -j`nproc` O=../build/```. The kernel will be built in ./kernel/build/

## Running the new kernel image and device tree
1. `scp ./kernel/build/arch/arm64/boot/Image <user>@<board_ip>:/boot/`
2. `scp ./kernel/build/arch/arm64/boot/dts/compulab/<device_tree> <user>@<board_ip>:/run/media/boot-mmcblk1p1/`
3. Reboot the iMX93 and enter the U-Boot terminal.
4. Select the device tree: `editenv fdtfile`
