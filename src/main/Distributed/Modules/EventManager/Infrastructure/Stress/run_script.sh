#!/bin/bash

# Define the path to the virtual environment
venv_path="./venv"


# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Function to check and install stress-ng
check_install_stress_ng() {
    if ! command -v stress-ng &> /dev/null; then
        echo "stress-ng is not installed. Installing..."
        # Add installation commands for stress-ng based on the system
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get install -y stress-ng || sudo yum install -y stress-ng
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew install stress-ng
        else
            echo "Unsupported OS for automatic installation of stress-ng."
            return 1
        fi
    fi
}

# Function to check and install python3-venv if necessary
install_python3_venv() {
    # Check if python3-venv is installed
    dpkg -s python3-venv &> /dev/null

    if [ $? -ne 0 ]; then
        echo "python3-venv package is not installed. Attempting to install..."
        # Attempt to install python3-venv
        sudo apt-get update && sudo apt-get install python3-venv -y

        # Check if the installation was successful
        if [ $? -ne 0 ]; then
            echo "Failed to install python3-venv. Please install it manually."
            exit 1
        fi
    else
        echo "python3-venv package is already installed."
    fi
}

# Create a virtual environment for isolation of dependencies from the system
create_venv() {
    # Check if the virtual environment already exists
    if [[ ! -d "$venv_path" ]]; then
        echo "Creating virtual environment..."
        python3 -m venv "$venv_path"
        chmod +x $venv_path

    else
        echo "Virtual environment already exists."
    fi
}

# Function to deactivate the virtual environment
deactivate_venv() {
    echo "Deactivating virtual environment..."
    deactivate 2>/dev/null
}

# Function to check and install missing dependencies from requirements.txt
install_missing_dependencies() {
    local requirements_file="requirements.txt"
    if [[ -f "$requirements_file" ]]; then
        echo "Installing dependencies from $requirements_file"
        source "$venv_path/bin/activate"  # Activate the virtual environment
        python -m pip install -r "$requirements_file"  # Use pip inside the virtual environment
        deactivate  # Deactivate the virtual environment
    else
        echo "The file $requirements_file does not exist."
        return 1
    fi
}

# Call the function to ensure python3-venv is installed
install_python3_venv

# Create and activate the virtual environment
create_venv

# Trap signals INT and TERM to ensure the virtual environment is deactivated
trap deactivate_venv INT TERM

# Check and install stress-ng and missing dependencies
check_install_stress_ng
install_missing_dependencies

# Run the Python script in a subshell with the virtual environment activated to make sure that the virtual environment is deactivated after the script finishes
(
    source "$venv_path/bin/activate"
    python3 StressHandlerModule.py
)
