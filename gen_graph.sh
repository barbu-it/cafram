#!/bin/bash
# Generate project class graph

set -eu
pyreverse -d docs/_static/ -o svg -p cafram -A cafram
echo "INFO: Graphs generated into: docs/_static/"

