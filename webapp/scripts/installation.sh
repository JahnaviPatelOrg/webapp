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
sudo apt-get install -y python3 python3-pip python3-virtualenv python3-full pipx

# Install other packages.
echo "Installing other packages."
sudo apt-get install -y mysql-server unzip libmysqlclient-dev pkg-config libmysqlclient-dev





