#!/bin/bash
  set -e

  # Install necessary packages
  sudo apt-get update
  sudo apt-get install -y wget unzip

  # Download and install CloudWatch agent
  wget https://amazoncloudwatch-agent.s3.amazonaws.com/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
  sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
  sudo rm ./amazon-cloudwatch-agent.deb

  # Create directory for config if it doesn't exist
  sudo mkdir -p /opt/aws/amazon-cloudwatch-agent/etc/

  # Return success
  echo "CloudWatch Agent installed successfully"