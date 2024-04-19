# variables.tf

variable "aws_key" {
  description = "AWS Access Key"
  type        = string
  sensitive   = true
}

variable "aws_skey" {
  description = "AWS Secret Key"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "us-west-2"
}
variable "DB_HOST" {
  description = "Database host URL"
  type        = string
}

variable "DB_NAME" {
  description = "Database name"
  type        = string
}

variable "DB_PASSWORD" {
  description = "Database password"
  type        = string
  sensitive   = true  # Marking the variable as sensitive to prevent it from being logged in plain text
}

variable "DB_PORT" {
  description = "Database port"
  type        = string
}

variable "DB_USER" {
  description = "Database user"
  type        = string
}
