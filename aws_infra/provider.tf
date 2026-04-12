terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "region_name" 
  shared_config_files      = ["C:\\Users\\username\\.aws\\config"]
  shared_credentials_files = ["C:\\Users\\username\\.aws\\credentials"]
  profile                  = "project_name"
}
