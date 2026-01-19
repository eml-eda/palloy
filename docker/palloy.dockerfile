FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

# ------------------------------------------------------------
# System dependencies
# ------------------------------------------------------------
RUN apt-get update && apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    git \
    curl \
    build-essential cmake build-essential git doxygen python3-pip libsdl2-dev curl cmake gtkwave libsndfile1-dev rsync autoconf automake texinfo libtool pkg-config libsdl2-ttf-dev wget doxygen \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
RUN pip3 install numpy matplotlib prettytable rich

# ------------------------------------------------------------
# Install PULP RISC-V 32-bit bare-metal toolchain
# ------------------------------------------------------------

WORKDIR /opt
RUN curl -L https://github.com/pulp-platform/pulp-riscv-gnu-toolchain/releases/download/v1.0.16/v1.0.16-pulp-riscv-gcc-ubuntu-18.tar.bz2 \
    -o riscv32.tar.bz2
RUN tar -xf riscv32.tar.bz2 
RUN mv ./v1.0.16-pulp-riscv-gcc-ubuntu-18 ./pulp_toolchain
RUN rm riscv32.tar.bz2

ENV RISCV_GCC=/opt/pulp_toolchain
ENV PATH=${RISCV_GCC}/bin:${PATH}
ENV PULP_RISCV_GCC_TOOLCHAIN=${RISCV_GCC}

RUN riscv32-unknown-elf-gcc --version

# ------------------------------------------------------------
# Workspace
# ------------------------------------------------------------
WORKDIR /workspace
RUN git clone https://github.com/eml-eda/palloy.git

WORKDIR /workspace/palloy
RUN git submodule update --init --recursive || echo "git submodule init failed (continuing)"
RUN git submodule update --recursive
RUN bash ./venv.sh || echo "venv.sh failed (continuing)"
