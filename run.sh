#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Parse arguments
USE_CONDA=false
for arg in "$@"; do
    if [ "$arg" == "--conda" ]; then
        USE_CONDA=true
    fi
done

# Activate the appropriate environment
if [ "$USE_CONDA" == true ]; then
    echo "Activating Conda environment..."
    if command_exists conda; then
        source activate ./venv
    else
        echo "Conda is not installed! Install Conda and try again."
        exit 1
    fi
else
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo "Virtual environment does not exist! Run setup script first."
        exit 1
    fi
fi

# Handle script interruption (CTRL+C) and ensure environment deactivation
trap "echo 'Interrupt received, deactivating environment...'; if [ '$USE_CONDA' == 'true' ]; then conda deactivate; else deactivate; fi; exit 1" SIGINT SIGTERM

# Run webui.py
if [ -f "webui.py" ]; then
    echo "Starting web UI..."
    python webui.py
else
    echo "webui.py not found!"
    exit 1
fi

# Deactivate virtual environment after execution
if [ "$USE_CONDA" == true ]; then
    conda deactivate
else
    deactivate
fi

echo "Script completed."

