# Recipe metadata
SUMMARY = "Kimera-RPGO - Robust Pose Graph Optimization"
HOMEPAGE = "https://github.com/MIT-SPARK/Kimera-RPGO"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.BSD;md5=feadbde370d2743a1692fabaddb16b6b"

# Source code repository and specific commit to build
SRC_URI = "git://github.com/MIT-SPARK/Kimera-RPGO.git;protocol=https"
SRCREV = "c535e9ef87fa8b978c9434f8d1aa4dcb10110661"

# Dependencies required to build the library
DEPENDS = "cmake gtsam"

# Directory where the source code will be unpacked after fetching
S = "${WORKDIR}/git"

# Inherit the CMake class to handle CMake build systems
inherit cmake

# Ensure the static development package includes the shared library file (QA fix)
FILES:${PN}-staticdev += "${libdir}/libKimeraRPGO.so"

# Allows empty output package - for case of header-only libraries
ALLOW_EMPTY:${PN} = "1"
