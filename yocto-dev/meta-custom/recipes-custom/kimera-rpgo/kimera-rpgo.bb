# Recipe metadata
SUMMARY = "Kimera-RPGO - Robust Pose Graph Optimization"
HOMEPAGE = "https://github.com/MIT-SPARK/Kimera-RPGO"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.BSD;md5=feadbde370d2743a1692fabaddb16b6b"

# Source and branch
SRC_URI = "git://github.com/MIT-SPARK/Kimera-RPGO.git;protocol=https"
SRCREV = "c535e9ef87fa8b978c9434f8d1aa4dcb10110661"

# Dependencies
DEPENDS = "cmake gtsam"

# Specify the directory to fetch the source code
S = "${WORKDIR}/git"

# Inherit classes
inherit cmake

FILES:${PN}-staticdev += "${libdir}/libKimeraRPGO.so"

ALLOW_EMPTY:${PN} = "1"
