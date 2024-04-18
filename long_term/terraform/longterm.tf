# Pipeline task definition

data "aws_iam_role" "execution-role" {
    name = "ecsTaskExecutionRole"
}

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
                    "value": var.AWS_KEY
                },
                 {
                    "name": "AWS_SECRET_ACCESS_KEY",
                    "value": var.AWS_SKEY
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
