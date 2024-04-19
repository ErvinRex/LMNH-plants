# variables.tf

variable "AWS_KEY" {
  description = "AWS Access Key"
  type        = string
  sensitive   = true
}

variable "AWS_SKEY" {
  description = "AWS Secret Key"
  type        = string
  sensitive   = true
}

variable "aws_region" {
  description = "AWS Region"
  type        = string
  default     = "eu-west-2"
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
  sensitive   = true  
}

variable "DB_PORT" {
  description = "Database port"
  type        = string
}

variable "DB_USER" {
  description = "Database user"
  type        = string
}
