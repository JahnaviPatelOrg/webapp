packer {
  required_plugins {
    amazon = {
      version = ">= 1.0.0, < 2.0.0"
      source  = "github.com/hashicorp/amazon"
    }

    googlecompute = {
      source  = "github.com/hashicorp/googlecompute"
      version = ">= 1, < 2"
    }
  }
}

variable "source_ami" {
  type = string
}

variable "account_ids" {
  type        = list(string)
  description = "List of AWS account IDs"
}

variable "google_project_id" {
  type = string
}

variable "db_host" {
  type = string
}

variable "db_user" {
  type = string
}

variable "db_password" {
  type = string
}

variable "db_name" {
  type = string
}

variable "secret_key" {
  type = string
}


source "amazon-ebs" "ubuntu" {
  ami_name        = "webapp-ami"
  ami_description = "Webapp AMI packer"
  instance_type   = "t2.micro"
  region          = "us-east-1"

  aws_polling {
    delay_seconds = 120
    max_attempts  = 50
  }

  ssh_username     = "ubuntu"
  ssh_wait_timeout = "10m"
  source_ami       = var.source_ami


  launch_block_device_mappings {
    device_name           = "/dev/sda1"
    volume_size           = 8
    volume_type           = "gp2"
    delete_on_termination = true
  }

  ami_users = var.account_ids

  tags = {
    Name        = "webapp-gmi"
    Description = "Webapp GMI packer"
  }
}

source "googlecompute" "ubuntu" {
  project_id          = var.google_project_id
  source_image_family = "ubuntu-2404-lts-amd64"
  image_description   = "Webapp GCE Image packer"
  ssh_username        = "ubuntu"
  zone                = "us-east1-b"
}


build {
  sources = [
    "source.amazon-ebs.ubuntu",
    #     "source.googlecompute.ubuntu"
  ]
  provisioner "shell" {
    script = "../scripts/installation.sh" # This script installs necessary dependencies and configurations
  }

  #   set up mysql database
  # Create the database and user if they do not exist.
  provisioner "shell" {
    environment_vars = [
      "DB_USER=${var.db_user}",
      "DB_PASSWORD=${var.db_password}",
      "DB_NAME=${var.db_name}",
      "DB_HOST=${var.db_host}",
    ]
    script = "../scripts/sql_setup.sh"
  }


  #  paste webapp.zip created by github action
  provisioner "file" {
    source      = "../../webapp.zip"
    destination = "/tmp/webapp.zip"
  }


  # Unzip the webapp.zip file to /opt/csye6225
  provisioner "shell" {
    inline = [
      "cd /tmp",
      "sudo unzip -o webapp.zip -d /opt/csye6225"
    ]
  }


  #   set up webapp
  provisioner "shell" {
    environment_vars = [
      "DB_USER=${var.db_user}",
      "DB_PASSWORD=${var.db_password}",
      "DB_NAME=${var.db_name}",
      "DB_HOST=${var.db_host}",
      "SECRET_KEY=${var.secret_key}"
    ]
    script = "../scripts/webapp_setup.sh"
  }
}
