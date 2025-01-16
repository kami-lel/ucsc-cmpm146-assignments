#!/bin/bash

# get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# check if python is installed
if ! command -v python &> /dev/null; then
    echo "Python could not be found, please ensure Python is installed and available in PATH."
    exit 1
fi

# run the Python script with relative paths
python "$SCRIPT_DIR/../src/nm_interactive.py" "$SCRIPT_DIR/../input/homer.png" "$SCRIPT_DIR/../input/homer.png.mesh.pickle" 2
