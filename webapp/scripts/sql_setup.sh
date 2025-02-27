#!/bin/bash

# Enable and start the MySQL service.
echo "Enabling and starting the MySQL service."
sudo systemctl enable mysql
sudo systemctl start mysql

# Create the database and user if they do not exist.
echo "Creating the database and user if they do not exist."
sudo mysql  -e "CREATE DATABASE IF NOT EXISTS $DB_NAME;"
sudo mysql  -e "CREATE USER IF NOT EXISTS '$DB_USER'@'$DB_HOST' IDENTIFIED BY '$DB_PASSWORD';"
sudo mysql  -e "GRANT ALL PRIVILEGES ON *.* TO '$DB_USER'@'$DB_HOST';"
sudo mysql  -e "FLUSH PRIVILEGES;"

