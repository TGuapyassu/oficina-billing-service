terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project     = "oficina"
      Environment = "prod"
      ManagedBy   = "terraform"
      Repository  = "oficina-infra-db"
    }
  }
}

module "vpc" {
  source      = "../../modules/vpc"
  name_prefix = "oficina-prod"
  cidr_block  = var.vpc_cidr
  azs         = var.availability_zones
}

module "rds" {
  source = "../../modules/rds"

  name_prefix                = "oficina-prod"
  vpc_id                     = module.vpc.vpc_id
  subnet_ids                 = module.vpc.private_subnet_ids
  allowed_cidr_blocks        = [module.vpc.vpc_cidr]
  allowed_security_group_ids = var.allowed_security_group_ids
  instance_class             = var.instance_class
  multi_az                   = true
  deletion_protection        = true
  skip_final_snapshot        = false
  backup_retention_period    = 14
}

variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "vpc_cidr" {
  type    = string
  default = "10.30.0.0/16"
}

variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b"]
}

variable "instance_class" {
  type    = string
  default = "db.t3.small"
}

variable "allowed_security_group_ids" {
  type    = list(string)
  default = []
}

output "vpc_id" {
  value = module.vpc.vpc_id
}

output "private_subnet_ids" {
  value = module.vpc.private_subnet_ids
}

output "public_subnet_ids" {
  value = module.vpc.public_subnet_ids
}

output "rds_endpoint" {
  value = module.rds.rds_endpoint
}

output "rds_port" {
  value = module.rds.rds_port
}

output "db_name" {
  value = module.rds.db_name
}

output "secret_arn" {
  value = module.rds.secret_arn
}

output "rds_security_group_id" {
  value = module.rds.security_group_id
}
