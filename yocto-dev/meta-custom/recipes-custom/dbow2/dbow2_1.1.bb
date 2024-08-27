# Recipe metadata
SUMMARY = "DBoW2 - An efficient and flexible C++ library for indexing and converting images into binary bag-of-words representations"
HOMEPAGE = "https://github.com/dorian3d/DBoW2"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=a40f1140f1638a6a38ba967cd7c95f83"

# Source code repository and specific commit to build
SRC_URI = "git://github.com/dorian3d/DBoW2.git;protocol=https"
SRCREV = "3924753db6145f12618e7de09b7e6b258db93c6e"

# Dependencies required to build the library
DEPENDS = "cmake opencv"

# Directory where the source code will be unpacked after fetching
S = "${WORKDIR}/git"

# Inherit the CMake class to handle CMake build systems
inherit cmake

# Ensure the static development package includes the shared library file (QA fix)
FILES:${PN}-staticdev += "${libdir}/libDBoW2.so"

# Allows empty output package - for case of header-only libraries
ALLOW_EMPTY:${PN} = "1"
