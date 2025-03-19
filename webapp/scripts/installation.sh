#!/bin/bash

# Update the package lists for upgrades for packages that need upgrading.
echo "Updating the package lists for upgrades for packages that need upgrading."
export DEBIAN_FRONTEND=noninteractive
sudo apt-get update -y

# Upgrade the packages on the system.
echo "Upgrading the packages on the system."
sudo apt-get upgrade -y

# Install Python and its package manager.
echo "Installing Python and its package manager."
sudo apt install -y python3-dev python3-pip python3-venv build-essential libjpeg-dev zlib1g-dev libpng-dev libfreetype6-dev

# Install other packages.
echo "Installing other packages."
sudo apt-get install -y unzip libmysqlclient-dev pkg-config libmysqlclient-dev





