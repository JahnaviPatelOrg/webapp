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


variable "region" {
  type    = string
  default = "us-east-1"
}

variable "source_ami" {
  type = string
}

variable "instance_type" {
  type    = string
  default = "t2.micro"
}

variable "ami_name" {
  type        = string
  description = "AMI for Assignment 4"
}

variable "ami_description" {
  type    = string
  default = "Webapp AMI packer"
}

variable "ssh_username" {
  type = string
}

variable "volume_type" {
  type    = string
  default = "gp2"
}

variable "account_ids" {
  type        = list(string)
  description = "List of AWS account IDs"
}

variable "google_project_id" {
  type = string
}

variable "source_image_family" {
  type = string
}

variable "gcpregion" {
  type    = string
  default = "us-east1-b"
}

source "amazon-ebs" "ubuntu" {
  ami_name        = var.ami_name
  ami_description = var.ami_description
  instance_type   = var.instance_type
  region          = var.region

  aws_polling {
    delay_seconds = 120
    max_attempts  = 50
  }

  ssh_username     = var.ssh_username
  ssh_wait_timeout = "10m"
  source_ami       = var.source_ami


  launch_block_device_mappings {
    device_name           = "/dev/sda1"
    volume_size           = 8
    volume_type           = var.volume_type
    delete_on_termination = true
  }

  ami_users = var.account_ids

  tags = {
    Name        = "webapp-ami"
    Description = "Webapp AMI packer"
  }
}

source "googlecompute" "ubuntu" {
  project_id          = var.google_project_id
  source_image_family = var.source_image_family
  image_description   = var.ami_description
  ssh_username        = var.ssh_username
  zone                = var.gcpregion
}


build {
  sources = [
    "source.amazon-ebs.ubuntu",
    "source.googlecompute.ubuntu"
  ]

  provisioner "shell" {
    script = "../scripts/installation.sh" # This script installs necessary dependencies and configurations
  }


}
