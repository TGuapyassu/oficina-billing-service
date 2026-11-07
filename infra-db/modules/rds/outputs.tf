output "rds_endpoint" {
  value = aws_db_instance.this.address
}

output "rds_port" {
  value = aws_db_instance.this.port
}

output "db_name" {
  value = var.db_name
}

output "db_username" {
  value = var.db_username
}

output "security_group_id" {
  value = aws_security_group.rds.id
}

output "secret_arn" {
  value = aws_secretsmanager_secret.db.arn
}

output "db_instance_arn" {
  value = aws_db_instance.this.arn
}

output "db_instance_id" {
  value = aws_db_instance.this.id
}
