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
sudo apt-get install -y python3 python3-pip python3-venv python-is-python3

# Install other packages.
echo "Installing other packages."
sudo apt-get install -y mysql-server unzip pkg-config libmysqlclient-dev

# Enable and start the MySQL service.
echo "Enabling and starting the MySQL service."
sudo systemctl enable mysql
sudo systemctl start mysql

#Create a new Linux group for the application if it does not exist.
echo "Creating a new Linux group for the application if it does not exist."
sudo groupadd -f csye6225

#Create a new Linux user for the application if it does not exist.
echo "Creating a new Linux user for the application if it does not exist."
sudo useradd -m -g csye6225 -s /usr/sbin/nologin csye6225

