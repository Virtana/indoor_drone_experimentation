# Recipe metadata
SUMMARY = "OpenGV - A collection of computer vision algorithms for solving geometric vision problems"
HOMEPAGE = "https://github.com/laurentkneip/opengv"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://License.txt;md5=4c8da07d2e1fc46899c78fdb56d238c5"

# Source code repository and specific commit to build
SRC_URI = "git://github.com/laurentkneip/opengv.git;protocol=https"
SRCREV = "91f4b19c73450833a40e463ad3648aae80b3a7f3"

# Dependencies required to build the library
DEPENDS = "libeigen gtsam"

# Directory where the source code will be unpacked after fetching
S = "${WORKDIR}/git"

# Inherit the CMake class to handle CMake build systems
inherit cmake

# CMake build options
EXTRA_OECMAKE = "\
    -DCMAKE_BUILD_TYPE=Release \
    -DEIGEN_INCLUDE_DIRS=${STAGING_DIR_TARGET}${includedir}/eigen3 \
    -DEIGEN_INCLUDE_DIR=${STAGING_DIR_TARGET}${includedir}/eigen3 \
"

# Allows empty output package - for case of header-only libraries
ALLOW_EMPTY:${PN} = "1"
