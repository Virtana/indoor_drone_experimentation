**Yocto Development**

This folder includes all relevant artifacts for setting up an independent Yocto development environment for project Ice Cream:
- Custom Yocto layer for additional/modified recipes for IMX image
- Standard configuration files for each development machine
- Miscellaneous image related scripts 

**How to setup?**

- Configure environment prerequisites for Yocto. 
    - Install on [local environment](https://docs.yoctoproject.org/brief-yoctoprojectqs/index.html#yocto-project-quick-build) OR
    - Utilize Compulab's [Docker containers](https://github.com/compulab-yokneam/yocker). This should be selected for Yocto version - Kirkstone.
- Import and set up Compulab's BSP for the IMX9
    - Follow [instructions](https://github.com/compulab-yokneam/meta-bsp-imx9/tree/kirkstone-2.2.0) up to _**"Setup build environment"**_.
    - The root of this directory will notably include a build and sources folder. 
- In new build folder, substitute _bblayers.conf_ and _local.conf_ for their respective files in this repo's `/build_conf` folder. 
    - _bblayers.conf_ - Defines the layers referenced by bitbake 
    - _local.conf_ - Defines the recipes referenced by bitbake
- In the sources folder, we need to import additional layers:
    - Clone this **indoor_drone_experimentation** repo.
    - Clone the [meta-ros](https://github.com/ros/meta-ros/tree/kirkstone) (kirkstone branch) in sources: 

**Building a SOM image on your Machine**
Every time you restart your computer OR enter the Docker dev container, you need to source the build folder:
`source compulab-setup-env {BUILD_FOLDER_NAME}`

To build the image: 
`bitbake imx-image-core`

Please note the minimum hardware criteria for Yocto builds. See [i.MX Yocto Project User's Guide](https://www.nxp.com/docs/en/user-guide/IMX_YOCTO_PROJECT_USERS_GUIDE.pdf)  for alternative images options (Section 5.2).
