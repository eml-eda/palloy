#!/bin/bash

###############################################################################
# This script is used to build and run the gvsoc simulator with a test binary #
###############################################################################

APP_DIR="/home/lelez/git/palloy/pulp-sdk/applications/MobileNetV1/"
NUM_CLUSTER_CORES=4

CONFIG="palloy.sh"
TARGET="palloy"
VENV_DIR="./.venv/"

###############################################################################

APP_DIR="$(realpath "$APP_DIR")"
# Activate the GVSoC venv
source "${VENV_DIR}bin/activate" && \

# Source config
echo "Sourcing $CONFIG config..." && \
source ./pulp-sdk/configs/$CONFIG && \

# Build the target
cd "./gvcuck/" && \
echo "Building ${TARGET} GVSoC target..." && \
make TARGETS=$TARGET build && \

# Go into app directory
cd $APP_DIR && \
make clean && \
make all CORE=$NUM_CLUSTER_CORES && \

# Run GVSoC
echo "Running GVSoC..." && \
make run && \

echo "Simulation ended."