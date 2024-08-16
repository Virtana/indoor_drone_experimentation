FROM ubuntu:22.04

RUN apt update
RUN apt -y install build-essential
RUN apt -y install wget

RUN wget https://armkeil.blob.core.windows.net/developer/Files/downloads/gnu-a/9.2-2019.12/binrel/gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu.tar.xz
RUN tar -C /opt -xf ./gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu.tar.xz

ENV ARCH=arm64
ENV CROSS_COMPILE=/opt/gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-

RUN mkdir -p /compulab_kernel/build
WORKDIR /compulab_kernel

ENV MACHINE=ucm-imx93

RUN apt -y install git

# Dependencies for kernel build
# See https://wiki.ubuntu.com/Kernel/BuildYourOwnKernel
RUN apt -y install libncurses-dev
RUN apt -y install gawk
RUN apt -y install flex
RUN apt -y install bison
RUN apt -y install openssl
RUN apt -y install libssl-dev
RUN apt -y install dkms
RUN apt -y install libelf-dev
RUN apt -y install libudev-dev
RUN apt -y install libpci-dev
RUN apt -y install libiberty-dev
RUN apt -y install autoconf
RUN apt -y install llvm
RUN apt -y install bc
RUN apt -y install cpio
RUN apt -y install rsync
RUN apt -y install libncursesw5
RUN apt -y install libpython2.7

RUN touch /root/.bash_aliases
RUN echo "alias gdb='/opt/gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu/bin/aarch64-none-linux-gnu-gdb /compulab_kernel/build/vmlinux -tui'" >> /root/.bash_aliases


WORKDIR /compulab_kernel/linux-compulab
