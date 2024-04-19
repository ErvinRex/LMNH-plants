# Infrastructure as Code

Instead of clicking around in the cloud in a non-repeatable and (sometimes) confusing way, store your cloud configuration as code.

This brings all the benefits of code (versioning, sharing, updating) to the cloud.

## Terraform

- Describe exactly what cloud resources you want
- Build them automatically
- Destroy them automatically
- Share your configuration easily with other people

This is a configuration tool, not a language.

## Required installations

- Terraform ('brew install terraform') - this allows you to run `terraform` in the terminal

### Setup

- Create a `main.tf` file
- Add a `provider` block with AWS config details
- Run `terraform init` to get the folder set up for terraforming
- Run `terraform plan` to see what your config would build
- Run `terraform apply` to actually build your infrastructure
- Run `terraform destroy` to shut down and clean up all resources

## Basic data config 

```sh
data "aws_db_subnet_group" "public_subnet_group" {
    name = ""
}

data "aws_vpc" "[your_vpc]" {
    id = "vpc-XXXX"
}
```

## Basic security group config

```sh
resource "aws_security_group" "rds_security_group" {


    name = "[xxx]-sg"
    description = "Allows inbound [x] access"
    vpc_id = data.aws_vpc.[your_vpc].id

    ingress {
        cidr_blocks       = ["0.0.0.0/0"]
        from_port         = 80
        protocol          = "tcp"
        to_port           = 80
    }
}
```