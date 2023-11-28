FROM ubuntu:20.04

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

RUN apt-get update -y && \
    apt upgrade -y

RUN apt-get install -y tzdata

RUN apt install -y bc
RUN apt install -y build-essential
RUN apt install -y chrpath
RUN apt install -y cpio
RUN apt install -y debianutils
RUN apt install -y diffstat
RUN apt install -y g++-multilib
RUN apt install -y gawk
RUN apt install -y gcc
RUN apt install -y gcc-multilib
RUN apt install -y git
RUN apt install -y iputils-ping
RUN apt install -y libegl1-mesa
RUN apt install -y libncurses5-dev
RUN apt install -y libsdl1.2-dev 
RUN apt install -y mesa-common-dev
RUN apt install -y pylint3
RUN apt install -y python3
RUN apt install -y python3-dev
RUN apt install -y python3-git
RUN apt install -y python3-jinja2
RUN apt install -y python3-pexpect
RUN apt install -y python3-pip
RUN apt install -y python3-subunit
RUN apt install -y socat
RUN apt install -y tar
RUN apt install -y texinfo
RUN apt install -y tmux
RUN apt install -y unzip
RUN apt install -y vim
RUN apt install -y wget
RUN apt install -y xsltproc
RUN apt install -y xterm
RUN apt install -y openssl
RUN apt install -y tree
RUN apt install -y xz-utils
RUN apt install -y zstd
RUN apt install -y liblz4-tool
RUN apt install -y file
RUN apt install -y locales
RUN apt install -y libacl1

# bc \
# build-essential \
# chrpath \
# cpio \
# debianutils \
# diffstat \
# dos2unix \ - ignoring
# g++-multilib \
# gawk \
# gcc \
# gcc-multilib \
# git \
# iputils-ping \
# libegl1-mesa \
# libncurses5-dev \
# libsdl1.2-dev \
# mesa-common-dev \
# pylint3 \
# python3 \
# python3-dev \
# python3-git \
# python3-jinja2 \
# python3-pexpect \
# python3-pip \
# python3-subunit \
# socat \
# tar \
# texinfo \
# tmux \
# unzip \
# vim \
# wget \
# xsltproc \
# xterm \
# openssl \
# tree \
# xz-utils \
# zstd \
# liblz4-tool \
# file \
# locales \
# libacl1


# Reference https://digitalgateamg.com/blog/2021/11/14/yocto-development-environment-with-docker/
RUN apt-get update && apt-get install -y \
    apt-utils locales sudo && \
    dpkg-reconfigure locales && \
    locale-gen en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
ENV LANG en_US.utf8

ARG host_uid=1001
ARG host_gid=1001
ENV USER_NAME sarika

RUN groupadd -g $host_gid $USER_NAME && \
    useradd -g $host_gid -m -s /bin/bash -u $host_uid $USER_NAME

# RUN groupadd -g $host_gid $USER_NAME && \
#     useradd -g $host_gid -m -s /bin/bash -p $(openssl passwd -crypt $PASS) -u $host_uid $USER_NAME

RUN echo "build ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

USER $USER_NAME
