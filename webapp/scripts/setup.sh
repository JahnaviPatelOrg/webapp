#!/bin/bash

# Update the package lists for upgrades for packages that need upgrading.
echo "Updating the package lists for upgrades for packages that need upgrading."
apt-get update -y

# Upgrade the packages on the system.
echo "Upgrading the packages on the system."
apt-get upgrade -y  --force-confnew

# Install Python and its package manager.
echo "Installing Python and its package manager."
apt-get install -y python3 python3-pip python3-venv python-is-python3

# Install other packages.
echo "Installing other packages."
apt-get install -y mysql-server unzip pkg-config libmysqlclient-dev

# Enable and start the MySQL service.
echo "Enabling and starting the MySQL service."
systemctl enable mysql
systemctl start mysql

cd /tmp || exit

# Extract database credentials from .env file
DB_USER=$(grep 'DB_USER' .env | cut -d '=' -f2 | tr -d "'")
DB_PASSWORD=$(grep 'DB_PASSWORD' .env | cut -d '=' -f2 | tr -d "'")
DB_HOST=$(grep 'DB_HOST' .env | cut -d '=' -f2 | tr -d "'")
DB_PORT=$(grep 'DB_PORT' .env | cut -d '=' -f2 | tr -d "'")

# Create the database and user if they do not exist.
echo "Creating the database and user if they do not exist."
mysql -u root -e "CREATE DATABASE IF NOT EXISTS csye6225;"
mysql -u root -e "CREATE USER IF NOT EXISTS '$DB_USER'@'$DB_HOST' IDENTIFIED BY '$DB_PASSWORD';"
mysql -u root -e "GRANT ALL PRIVILEGES ON *.* TO '$DB_USER'@'$DB_HOST';"
mysql -u root -e "FLUSH PRIVILEGES;"

cd ..


#Create a new Linux group for the application if it does not exist.
echo "Creating a new Linux group for the application if it does not exist."
groupadd -f csye6225

#Create a new Linux user for the application if it does not exist.
echo "Creating a new Linux user for the application if it does not exist."
useradd -m -g csye6225 -s /usr/sbin/nologin csye6225

# Create directory for the web application  in /opt/csye6225 directory.
mkdir -p /opt/csye6225
unzip /tmp/webapp.zip -d /opt/csye6225

# Change the ownership of the directory to the new user and group.
chown -R csye6225:csye6225 /opt/csye6225

# Update the permissions of the folder and artifacts in the directory.
chmod -R 755 /opt/csye6225

#move .env file to /opt/csye6225/webapp
cp /tmp/.env /opt/csye6225/webapp
chown csye6225:csye6225 /opt/csye6225/webapp/.env
chmod 600 /opt/csye6225/webapp/.env

# Go to the directory where the web application is installed.
cd /opt/csye6225/webapp || exit

# Create a virtual environment for the application.
python3 -m venv venv

# Activate the virtual environment.
source venv/bin/activate

# Install the required packages.
pip3 install -r requirements.txt

#store vm_ip address
VM_IP=$(grep 'VM_IP' .env | cut -d '=' -f2 | tr -d "'")

# Go to the directory where the web application is installed.
cd webapp || exit

# Run migrations.
python3 manage.py makemigrations
python3 manage.py migrate

#test the application
python3 manage.py test

# run the server on vm ip and port 8080
python3 manage.py runserver $VM_IP:8080


