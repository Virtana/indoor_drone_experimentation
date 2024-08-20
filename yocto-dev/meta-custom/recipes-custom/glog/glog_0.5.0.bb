# Recipe for adding Google glog to a custom Yocto layer
# Modified from the original recipe in meta-openembedded to include custom setting
# Original - https://github.com/openembedded/meta-openembedded/blob/kirkstone/meta-oe/recipes-support/glog/glog_0.5.0.bb

DESCRIPTION = "The glog library implements application-level logging. This \
library provides logging APIs based on C++-style streams and various helper \
macros."
HOMEPAGE = "https://github.com/google/glog"

LICENSE = "BSD-3-Clause"
LIC_FILES_CHKSUM = "file://COPYING;md5=dc9db360e0bbd4e46672f3fd91dd6c4b"

SRC_URI = " \
    git://github.com/google/glog.git;nobranch=1;protocol=https \
    file://libexecinfo.patch \
"

SRCREV = "8f9ccfe770add9e4c64e9b25c102658e3c763b73"

S = "${WORKDIR}/git"

# added DEPENDS so that it can be built and linked with gflags
DEPENDS = " gflags "

EXTRA_OECMAKE += "-DWITH_GFLAGS=ON"

inherit cmake

PACKAGECONFIG ?= "shared unwind"
PACKAGECONFIG:remove:riscv64 = "unwind"
PACKAGECONFIG:remove:riscv32 = "unwind"
PACKAGECONFIG:append:libc-musl:riscv64 = " execinfo"
PACKAGECONFIG:append:libc-musl:riscv32 = " execinfo"

PACKAGECONFIG[unwind] = "-DWITH_UNWIND=ON,-DWITH_UNWIND=OFF,libunwind,libunwind"
PACKAGECONFIG[execinfo] = ",,libexecinfo"
PACKAGECONFIG[shared] = "-DBUILD_SHARED_LIBS=ON,-DBUILD_SHARED_LIBS=OFF,,"

do_configure:append() {
    # remove WORKDIR info to improve reproducibility
    if [ -f  "${B}/config.h" ] ; then
        sed -i 's/'$(echo ${WORKDIR} | sed 's_/_\\/_g')'/../g' ${B}/config.h
    fi
}
