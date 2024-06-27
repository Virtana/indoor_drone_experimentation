## Repository setup: Cloning the repository and managing the linux-compulab submodule
To clone the `indoor_drone_experimentation` repo, run the following command:
```
git clone git@github.com:Virtana/indoor_drone_experimentation.git
```
Ensure the `linux-compulab` submodule is update to date by running the following:
```
cd indoor_drone_experimentation
git submodule update –init –recursive
```

When changing branches on indoor_drone_experimentation, run the same `git submodule update` command to make sure linux-compulab is in sync.


## Building the kernel

Running the `build_container.sh` script creates a docker container with all relevant dependencies. `run_container.sh` then runs the same container. In the terminal, you should be in the `/compulab_kernel/linux-compulab` directory. 

Follow [compulab instructions](https://github.com/compulab-yokneam/meta-bsp-imx9/blob/kirkstone-2.2.0-yocto-r1.1/Documentation/linux_kernel_build.m) for kernel compilation:

```
make ${MACHINE}_defconfig O=../build/
make -j8 O=../build/
```

## Device Tree Edits
Scp the new device tree (dtb) to /run/media/boot-<partition>.

To get the the U-boot terminal, you need to press any key to prevent autoboot during startup. You need to be connected via a _serial terminal application_ (as oppsosed to SSH) to get this option. 

From U-Boot, run `editenv fdtfile` and enter the name of the new dtb file that you added to the boot partition. 

Run with new Image file using the following command:
```
run bsp_bootcmd
```

## Commands that should allow image capture via V4L2
V4l2 capture:
v4l2-ctl --device /dev/video0 --stream-mmap --stream-to=frame.raw --stream-count=1

v4l2-ctl --device /dev/video0 --list-formats-ext  
