#!/bin/bash
# One-time config for gvsoc installation
GVSOC_DIR="./gvcuck/"

# Create a venv environment
python3 -m venv .venv
source ".venv/bin/activate"

# Install dependencies
pip3 install -r $GVSOC_DIR/requirements.txt
pip3 install -r $GVSOC_DIR/core/requirements.txt
pip3 install -r $GVSOC_DIR/gapy/requirements.txt