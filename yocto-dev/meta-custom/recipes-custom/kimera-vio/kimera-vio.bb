SUMMARY = "Kimera-VIO: Visual-Inertial Odometry for Robust Autonomous Navigation"
HOMEPAGE = "https://github.com/MIT-SPARK/Kimera-VIO"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE.BSD;md5=feadbde370d2743a1692fabaddb16b6b"

SRC_URI = "git://github.com/Virtana/Kimera-VIO.git;protocol=https;branch=sarika/cross-compiling/docker"
SRCREV = "999620fbe9a942f94bec903a23388d7d3c928fd0"

# SRC_URI = "git://github.com/MIT-SPARK/Kimera-VIO.git;protocol=https"
# SRCREV = "2c7dff1941088e9fe9028f623afb2897451ff2ef"
# SRC_URI[sha256sum] = "25fa569e76927af1cbae940d9eb38944693f11a7266b4ac41d336e5fba5c730c"

S = "${WORKDIR}/git"

inherit cmake

DEPENDS = "boost gflags glog gtsam opengv opencv dbow2 kimera-rpgo gcc-runtime"

# Include additional CMake options
EXTRA_OECMAKE += "\
    -DKIMERA_BUILD_TESTS=OFF \
    -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
"

FILES:${PN}-staticdev += "${libdir}/libkimera_vio.so"
