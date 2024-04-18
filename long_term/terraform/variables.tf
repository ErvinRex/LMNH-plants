# Variable secrets on local terraform.tfvars file
variable "AWS_ACCESS_KEY_ID" {
    type = string
}

variable "AWS_SECRET_ACCESS_KEY" {
    type = string
}

variable "DB_USER" {
    type = string
}

variable "DB_PASSWORD" {
    type = string
}

variable "DB_NAME" {
    type = string
}

variable "DB_HOST" {
    type = string
}

variable "DB_PORT" {
    type = string
}

variable "DB_SCHEMA" {
    type = string
}