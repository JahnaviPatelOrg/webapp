#!/bin/bash

#Create a new Linux group for the application if it does not exist.
echo "Creating a new Linux group for the application if it does not exist."
sudo groupadd -f csye6225

# Create a new Linux user for the application if it does not exist.
echo "Creating a new Linux user for the application if it does not exist."
sudo useradd -m -g csye6225 -s /usr/sbin/nologin csye6225

# Create directory for the web application in /opt/csye6225 directory.
echo "Creating directory for the web application."
sudo mkdir -p /opt/csye6225
sudo unzip /tmp/webapp.zip -d /opt/csye6225


# Change the ownership of the directory to the new user and group.
echo "Changing the ownership of the directory to the new user and group."
sudo chown -R csye6225:csye6225 /opt/csye6225

# Update the permissions of the folder and artifacts in the directory.
echo "Updating the permissions of the folder and artifacts in the directory."
sudo chmod -R 755 /opt/csye6225

#make .venv file
echo "Creating .venv file"
sudo mkdir -p /opt/csye6225/webapp/.venv
#own the directory to csye6225
sudo chown -R csye6225:csye6225 /opt/csye6225/webapp/.venv
#update the permissions of the folder and artifacts in the directory.
sudo chmod -R 755 /opt/csye6225/webapp/.venv

# Go to the directory where the web application is installed.
echo "Going to the directory where the web application is installed."
cd /opt/csye6225/webapp || exit

# Create a virtual environment for the application.
echo "Creating a virtual environment for the application."
sudo python3 -m venv /opt/csye6225/venv

# Activate the virtual environment.
echo "Activating the virtual environment."
# Install the required packages.
echo "Installing the required packages."
sudo bash -c "source /opt/csye6225/venv/bin/activate && pip install -r requirements.txt"

#move the service file to /etc/systemd/system
echo "Moving the service file to /etc/systemd/system"
sudo cp /opt/csye6225/webapp/packer_setup/webapp.service /etc/systemd/system/webapp.service
sudo chown csye6225:csye6225 /etc/systemd/system/webapp.service

#start the server
echo "Starting the server."
sudo systemctl daemon-reload
sudo systemctl enable webapp
#sudo systemctl start webapp
#sudo systemctl status webapp



