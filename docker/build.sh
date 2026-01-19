#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

docker build -t palloy:latest -f "$SCRIPT_DIR/palloy.dockerfile" "$PROJECT_ROOT"
