variable "name_prefix" {
  type        = string
  description = "Prefixo dos recursos (ex.: oficina-homolog)"
}

variable "vpc_id" {
  type        = string
  description = "VPC onde o RDS será criado"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnets privadas para o DB subnet group"
}

variable "allowed_security_group_ids" {
  type        = list(string)
  description = "SGs que podem acessar a porta 5432 (Lambda, nodes EKS)"
  default     = []
}

variable "allowed_cidr_blocks" {
  type        = list(string)
  description = "CIDRs adicionais com acesso ao RDS (ex.: VPC CIDR)"
  default     = []
}

variable "db_name" {
  type    = string
  default = "oficina"
}

variable "db_username" {
  type    = string
  default = "oficina"
}

variable "instance_class" {
  type    = string
  default = "db.t3.micro"
}

variable "allocated_storage" {
  type    = number
  default = 20
}

variable "engine_version" {
  type    = string
  default = "16.4"
}

variable "multi_az" {
  type    = bool
  default = false
}

variable "backup_retention_period" {
  type    = number
  default = 7
}

variable "deletion_protection" {
  type    = bool
  default = false
}

variable "skip_final_snapshot" {
  type    = bool
  default = true
}

variable "tags" {
  type    = map(string)
  default = {}
}
