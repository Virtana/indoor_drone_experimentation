# Use an official Python runtime as a parent image
FROM ubuntu:18.04

# To avoid tzdata asking for geographic location...
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

# Set the working directory to /root
ENV DIRPATH /root
WORKDIR $DIRPATH

#Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN apt-get update && apt-get install -y git cmake

RUN apt-get install -y tzdata

# Installing cross-compiling dependencies
RUN apt update -y && \
    apt upgrade -y

RUN apt install -y wget
RUN apt install -y gcc
RUN apt install -y make
RUN apt install -y cmake
RUN apt install -y build-essential
RUN apt install -y gcc-aarch64-linux-gnu
RUN apt install -y g++-aarch64-linux-gnu
RUN apt install -y binutils-aarch64-linux-gnu

RUN apt update -y
RUN apt install -y perl

# GTSAM deps
RUN apt-get update && apt-get install -y libboost-all-dev

# # OpenCV deps
RUN apt-get update && apt-get install -y \
      build-essential cmake unzip pkg-config \
      libjpeg-dev libpng-dev libtiff-dev \
      libvtk6-dev \
      libgtk-3-dev \
      libatlas-base-dev gfortran

# # Cross-compiling CMake
# RUN git clone https://github.com/opencv/opencv.git
# RUN cd opencv && \
#       git checkout tags/3.3.1 && \
#       mkdir build

# RUN git clone https://github.com/opencv/opencv_contrib.git
# RUN cd opencv_contrib && \
#       git checkout tags/3.3.1

# cmake -DCMAKE_TOOLCHAIN_FILE=../aarch64-gnu.toolchain.cmake -DCMAKE_BUILD_TYPE=Release -D BUILD_opencv_python=OFF -D BUILD_opencv_python2=OFF -D BUILD_opencv_python3=OFF -DOPENCV_EXTRA_MODULES_PATH=/root/opencv_contrib/modules ../../..