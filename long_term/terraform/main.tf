# Create the cloud platform

provider "aws" {
    region = "eu-west-2"
    access_key = var.AWS_KEY
    secret_key = var.AWS_SKEY
}

data "aws_vpc" "cohort-10-vpc" {
    id = "vpc-0c4f01396d92e1cc7"
}

data "aws_ecs_cluster" "c10-ecs-cluster" {
    cluster_name = "c10-ecs-cluster"
}
