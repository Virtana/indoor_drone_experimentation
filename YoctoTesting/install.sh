#!/bin/bash -xe

#layers on which our image depends
POKY_REPO=git://git.yoctoproject.org/poky.git
OPENEMBEDDED_REPO=git://git.openembedded.org/meta-openembedded.git

# Setup all source directories
if [ ! -d /opt/build ] ; then
   git clone "$POKY_REPO" -b nanbield  /opt/build/poky
   git clone "$OPENEMBEDDED_REPO" -b nanbield /opt/build/meta-openembedded
fi

# initialize build directory
source /opt/build/poky/oe-init-build-env /opt/build

# add all required layers to the build
bitbake-layers add-layer meta-openembedded/meta*/
bitbake-layers add-layer /yocoto-dev-enviroment/layers/meta-imx/
# bitbake-layers add-layer /yocoto-dev-enviroment/layers/meta-aws/
# bitbake-layers add-layer /yocoto-dev-enviroment/layers/meta-custom-app/