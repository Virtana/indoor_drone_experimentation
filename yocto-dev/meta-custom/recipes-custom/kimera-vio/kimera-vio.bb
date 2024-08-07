SUMMARY = "Kimera-VIO: Visual-Inertial Odometry for Robust Autonomous Navigation"
HOMEPAGE = "https://github.com/MIT-SPARK/Kimera-VIO"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://LICENSE.BSD;md5=feadbde370d2743a1692fabaddb16b6b"

SRC_URI = "git://github.com/Virtana/Kimera-VIO.git;protocol=https;branch=david/kimera-recipe-fix"
SRCREV = "785a52ae6a1f1156a15b84378283e9f7e19e3811"

S = "${WORKDIR}/git"

inherit cmake pkgconfig

DEPENDS = "boost gflags glog gtsam opengv opencv dbow2 kimera-rpgo gcc-runtime"

# Include additional CMake options
EXTRA_OECMAKE += "\
    -DKIMERA_BUILD_TESTS=OFF \
    -DCMAKE_SYSTEM_PROCESSOR=aarch64 \
"

FILES:${PN}-staticdev += "${libdir}/libkimera_vio.so"

ALLOW_EMPTY:${PN} = "1"
