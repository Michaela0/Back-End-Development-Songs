#!/bin/bash
echo "****************************************"
echo " Resetting and Setting up Capstone Environment"
echo "****************************************"

echo "Removing existing virtual environment if any..."
rm -rf ~/venv

echo "Installing Python 3.9 and virtual environment tools..."
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3.9 python3.9-venv

echo "Creating a new Python virtual environment..."
python3.9 -m venv ~/venv

echo "Activating the virtual environment..."
source ~/venv/bin/activate

echo "Upgrading pip and wheel..."
pip install --upgrade pip wheel

echo "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

echo "Installing pytest..."
pip install pytest

echo "Setting up automatic activation in .bashrc..."
sed -i '/source ~\/venv\/bin\/activate/d' ~/.bashrc  # Remove old line if exists
echo "source ~/venv/bin/activate" >> ~/.bashrc

echo "****************************************"
echo " Capstone Environment Reset and Setup Complete"
echo "****************************************"
echo ""
echo "Please open a new terminal or run 'source ~/.bashrc' to activate the environment."
echo ""
