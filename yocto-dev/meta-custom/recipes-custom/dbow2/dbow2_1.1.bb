# Recipe metadata
SUMMARY = "DBoW2 - An efficient and flexible C++ library for indexing and converting images into binary bag-of-words representations"
HOMEPAGE = "https://github.com/dorian3d/DBoW2"
LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://LICENSE.txt;md5=a40f1140f1638a6a38ba967cd7c95f83"

# Source and branch
SRC_URI = "git://github.com/dorian3d/DBoW2.git;protocol=https"
SRCREV = "3924753db6145f12618e7de09b7e6b258db93c6e"

# Dependencies
DEPENDS = "cmake opencv"

# Specify the directory to fetch the source code
S = "${WORKDIR}/git"

# Inherit classes
inherit cmake

FILES:${PN}-staticdev += "${libdir}/libDBoW2.so"
