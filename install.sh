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

# Check for Python 3.10 or Conda
if [ "$USE_CONDA" == true ] || ! command_exists python3.10; then
    echo "Python 3.10 is not installed or --conda flag is used. Checking for Conda..."
    if command_exists conda; then
        echo "Conda is installed. Using Conda to create an environment."
        if [ ! -d "venv" ]; then
            echo "Creating Conda environment..."
            conda create --yes --prefix ./venv python=3.10
        else
            echo "Conda environment already exists."
        fi
        source activate ./venv
    else
        echo "Neither Python 3.10 nor Conda are installed! Install one and rerun the script."
        exit 1
    fi
else
    echo "Python 3.10 is installed. Using Python virtual environment."
    if [ ! -d "venv" ]; then
        echo "Creating virtual environment..."
        python3.10 -m venv venv
    else
        echo "Virtual environment already exists."
    fi
    source venv/bin/activate
fi

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "Installing required packages..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "requirements.txt file not found!"
fi

# Deactivate virtual environment
if [ "$USE_CONDA" == true ]; then
    conda deactivate
else
    deactivate
fi

echo "Script completed."
