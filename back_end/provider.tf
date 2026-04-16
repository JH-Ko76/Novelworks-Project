terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region = "ap-northeast-2" 
  shared_config_files      = ["C:\\Users\\KOHOME\\.aws\\config"]
  shared_credentials_files = ["C:\\Users\\KOHOME\\.aws\\credentials"]
  profile                  = "my-novelworks-project"
}
