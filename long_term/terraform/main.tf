# Create the cloud platform

provider "aws" {
    region = "eu-west-2"
    access_key = var.AWS_ACCESS_KEY_ID
    secret_key = var.AWS_SECRET_ACCESS_KEY
}

data "aws_vpc" "cohort-10-vpc" {
    id = "vpc-0c4f01396d92e1cc7"
}

data "aws_ecs_cluster" "c10-ecs-cluster" {
    cluster_name = "c10-ecs-cluster"
}

data "aws_ecr_repository" "upload-wipe-pipeline" {
    name = "ord-lmnh-upload/wipe-pipeline"
}

data "aws_iam_role" "execution-role" {
    name = "ecsTaskExecutionRole"
}

# Pipeline task definition

resource "aws_ecs_task_definition" "pipeline-task-def" {
    family = "ord-lmnh-upload-wipe-pipeline-terraform"
    requires_compatibilities = ["FARGATE"]
    network_mode = "awsvpc"
    memory = 3072
    cpu = 1024
    runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }
    execution_role_arn = data.aws_iam_role.execution-role.arn
    container_definitions = jsonencode([
        {
            name      = "ord-lmnh-upload-wipe-container"
            image     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/ord-lmnh-upload/wipe-pipeline:latest"
            essential = true
            portMappings = [
                {
                name = "ord-lmnh-upload-wipe-container-80-tcp"
                containerPort = 80
                hostPort      = 80
                protocol      = "tcp"
                appProtocol   = "http"
                }
            ]
            "environment": [
                {
                    "name": "AWS_ACCESS_KEY_ID",
                    "value": var.AWS_ACCESS_KEY_ID
                },
                 {
                    "name": "AWS_SECRET_ACCESS_KEY",
                    "value": var.AWS_SECRET_ACCESS_KEY
                },
                                 {
                    "name": "DB_HOST",
                    "value": var.DB_HOST
                },
                                 {
                    "name": "DB_NAME",
                    "value": var.DB_NAME
                },
                                 {
                    "name": "DB_PORT",
                    "value": var.DB_PORT
                },
                                 {
                    "name": "DB_USER",
                    "value": var.DB_USER
                },
                                 {
                    "name": "DB_PASSWORD",
                    "value": var.DB_PASSWORD
                }
            ]
        }
    ])
  }

# Eventbridge trigger for upload-wipe-pipeline

data "aws_iam_role" "eventbridge_execution_role" {
  name = "Amazon_EventBridge_Scheduler_ECS_16ba5186bf_ord_upload"
}

resource "aws_scheduler_schedule" "pipeline_schedule" {
  name       = "ord-lmnh-upload-wipe-pipeline-schedule"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 0 * * ? *)"

  target {
    arn      = data.aws_ecs_cluster.c10-ecs-cluster.arn
    role_arn = data.aws_iam_role.eventbridge_execution_role.arn
    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.pipeline-task-def.arn
      launch_type = "FARGATE"
      network_configuration {
        subnets = ["subnet-0f1bc89d0670672b5", "subnet-010c8f9ace38ac103", "subnet-05a01546985e339a6"]
        assign_public_ip = true
        security_groups = ["sg-0d3d4175fe23c85bd"]
      }
    }
  }
}

output "execution_role_arn" {
    value = aws_ecs_task_definition.pipeline-task-def.arn
}
   
