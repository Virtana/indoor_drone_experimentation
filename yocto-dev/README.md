# Yocto Development

This folder includes all relevant artifacts for setting up an independent Yocto development environment for creating our own custom images:
- Custom Yocto layer for additional/modified recipes for IMX image
- Standard configuration files for each development machine
- Miscellaneous image related scripts 

#### Setting up Development Environment

- Configure environment prerequisites for Yocto. 
    - You can install essential packages locally if you intend to run Yocto on your host machine. 
        ``` 
        For Ubuntu:
        $ sudo apt install gawk wget git diffstat unzip texinfo gcc build-essential chrpath socat cpio python3 python3-pip python3-pexpect xz-utils debianutils iputils-ping python3-git python3-jinja2 python3-subunit zstd liblz4-tool file locales libacl1
        $ sudo locale-gen en_US.UTF-8
        ```
        See [quick build guide](https://docs.yoctoproject.org/brief-yoctoprojectqs/index.html#yocto-project-quick-build) if you'd like more information.
    - OR Utilize Compulab's Ubuntu 20.04 (Preferred for Kirkstone) [Docker container](https://github.com/compulab-yokneam/yocker) for running the Yocto build environment inside.  
- Import and set up Compulab's BSP for the IMX9
    - Follow all README [instructions](https://github.com/compulab-yokneam/meta-bsp-imx9/tree/kirkstone-2.2.0) up to and including _**"Setup build environment"**_.
    - Verify that the root of the directory created above includes a `build` and `sources` folder. 
- In the build folder, substitute _bblayers.conf_ and _local.conf_ for their respective files in this repo's `yocto_dev/build_conf` folder. 
    - _bblayers.conf_ - Defines the layers referenced by bitbake 
    - _local.conf_ - Defines the recipes referenced by bitbake
    See [Yocto Project Concepts](https://docs.yoctoproject.org/4.0.20/singleindex.html#yocto-project-concepts) for more information on bitbake, these config files and more.
- In the sources folder, we need to import additional layers that are build prerequisites:
    - Clone this **indoor_drone_experimentation** repo to include dependencies and custom recipe for Kimera-VIO.
    - Clone the [meta-ros](https://github.com/ros/meta-ros/tree/kirkstone) (kirkstone branch) for GTSAM recipe dependencies.

#### Building a UCM-iMX93 image on your Machine
Every time you restart your computer OR enter the Docker dev container, you need to source the build folder:
`source compulab-setup-env {BUILD_FOLDER_NAME}`

To build the image: 
`bitbake imx-image-core`
