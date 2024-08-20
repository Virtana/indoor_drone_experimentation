# Recipe metadata
SUMMARY = "Kimera-VIO: Visual-Inertial Odometry for Robust Autonomous Navigation"
HOMEPAGE = "https://github.com/MIT-SPARK/Kimera-VIO"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE.BSD;md5=feadbde370d2743a1692fabaddb16b6b"

# Source code repository and specific commit to build
SRC_URI = "git://github.com/Virtana/Kimera-VIO.git;protocol=https;branch=david/kimera-recipe-fix"
SRCREV = "785a52ae6a1f1156a15b84378283e9f7e19e3811"

# Directory where the source code will be unpacked after fetching
S = "${WORKDIR}/git"

# Inherit the CMake class to handle CMake build system
inherit cmake pkgconfig

# Dependencies required to build the library
DEPENDS = "boost gflags glog gtsam opengv opencv dbow2 kimera-rpgo gcc-runtime"

# Include additional CMake options
EXTRA_OECMAKE += "\
    -DKIMERA_BUILD_TESTS=OFF \
    -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
"

# Ensure the static development package includes the shared library file (QA fix)
FILES:${PN}-staticdev += "${libdir}/libkimera_vio.so"

# Allows empty output package - for case of header-only libraries
ALLOW_EMPTY:${PN} = "1"
