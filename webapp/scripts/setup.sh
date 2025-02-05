#!/bin/bash

# Update the package lists for upgrades for packages that need upgrading.
apt-get update -y

# Upgrade the packages.
apt-get upgrade -y

# Install Python and its package manager.
apt-get install -y python3 python3-pip python3-venv python-is-python3

# Install other packages.
apt-get install -y mysql-server unzip pkg-config libmysqlclient-dev

# Enable and start the MySQL service.
systemctl enable mysql
systemctl start mysql

# Create the database and user.
mysql -u root -e "CREATE DATABASE csye6225;"

#Create a new Linux group for the application.
groupadd csye6225

#Create a new Linux user for the application.
useradd -m -g csye6225 -s /usr/sbin/nologin csye6225

# Create directory for the web application  in /opt/csye6225 directory.
mkdir -p /opt/csye6225
unzip /tmp/webapp.zip -d /opt/csye6225

# Change the ownership of the directory to the new user and group.
chown -R csye6225:csye6225 /opt/csye6225

# Update the permissions of the folder and artifacts in the directory.
chmod -R 755 /opt/csye6225

# Go to the directory where the web application is installed.
cd /opt/csye6225/webapp || exit

# Create a virtual environment for the application.
python3 -m venv venv

# Activate the virtual environment.
source venv/bin/activate

# Install the required packages.
pip3 install -r requirements.txt

# Go to the directory where the web application is installed.
cd webapp || exit

# Run migrations.
python3 manage.py makemigrations
python3 manage.py migrate

# Run the application.
python3 manage.py runserver





