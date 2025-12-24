#!/bin/bash

###############################################################################
# This script is used to build and run the gvsoc simulator with a test binary #
###############################################################################

APP_DIR="./pulp-sdk/applications/MobileNetV1/"
# APP_DIR="./pulp-sdk/tests/hello/"
NUM_CLUSTER_CORES=4

CONFIG="palloy.sh"
TARGET="palloy"
VENV_DIR="./.venv/"

export TRACE_FILE="$(dirname "$(readlink -f "$0")")/traces.log"

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
make all -B CORE=$NUM_CLUSTER_CORES && \

# Run GVSoC
echo "Running GVSoC..." && \
make run && \

echo "Simulation ended."

# Shrink traces file to last 10000 lines
tail -n 10000 $TRACE_FILE > ${TRACE_FILE}.tmp && mv ${TRACE_FILE}.tmp $TRACE_FILE && \
echo "Traces saved to $TRACE_FILE"