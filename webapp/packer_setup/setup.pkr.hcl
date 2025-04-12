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
  ami_name        = "webapp-ami-{{timestamp}}"
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
    script = "../scripts/installation.sh"
    # This script installs necessary dependencies and configurations
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
    script = "../scripts/webapp_setup.sh"
  }

  # Install and configure CloudWatch Agent
  # Install and configure CloudWatch Agent
  provisioner "shell" {
    script = "../scripts/install_cloudwatch_agent.sh"
  }

  # Configure StatsD for CloudWatch Agent
  provisioner "file" {
    content     = <<EOT
{
  "agent": {
    "metrics_collection_interval": 60,
    "run_as_user": "root"
  },
  "metrics": {
    "namespace": "WebApp",
    "append_dimensions": {
      "InstanceId": "$${aws:InstanceId}"
    },
    "metrics_collected": {
      "statsd": {
        "service_address": ":8125",
        "metrics_collection_interval": 10,
        "metrics_aggregation_interval": 60
      },
      "cpu": {
        "measurement": ["cpu_usage_idle", "cpu_usage_user", "cpu_usage_system"],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      },
      "mem": {
        "measurement": ["mem_used_percent"],
        "metrics_collection_interval": 60
      },
      "disk": {
        "measurement": ["used_percent"],
        "metrics_collection_interval": 60,
        "resources": ["*"]
      }
    }
  }
}
EOT
    destination = "/tmp/amazon-cloudwatch-agent.json"
  }

  provisioner "shell" {
    inline = [
      "sudo cp /tmp/amazon-cloudwatch-agent.json /opt/aws/amazon-cloudwatch-agent/etc/",
      "sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s",
      "sudo systemctl enable amazon-cloudwatch-agent"
    ]
  }

  post-processor "manifest" {
    output = "manifest.json"
  }

}
