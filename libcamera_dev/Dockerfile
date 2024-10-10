FROM ubuntu:20.04

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

RUN apt update
RUN apt upgrade -y

RUN apt install -y gcc-9-aarch64-linux-gnu
RUN apt install -y g++-9-aarch64-linux-gnu

RUN apt install -y git
RUN apt install -y cmake

# Dependencies for meson, which is used for building libcamera
RUN apt install -y python3 python3-pip python3-setuptools \
        python3-wheel ninja-build python3-venv

RUN pip install pyyaml meson jinja2 ply

# Installing libcamera
RUN git clone https://git.libcamera.org/libcamera/libcamera.git /libcamera 

WORKDIR /libcamera
COPY aarch64.txt /libcamera/
RUN meson build -Dprefix=/usr/ --cross-file ./aarch64.txt && \
        cd build && \
        ninja && \
        ninja install

WORKDIR /libcam_cross
