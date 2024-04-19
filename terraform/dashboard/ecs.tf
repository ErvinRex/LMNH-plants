

resource "aws_ecs_task_definition" "dashboard_task" {
  family                   = "ord-lmnh-plants-dashboard-terraform"
  network_mode             = "awsvpc"
  execution_role_arn       = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  cpu                      = "1024"
  memory                   = "3072"
  requires_compatibilities = ["FARGATE"]
  container_definitions    = jsonencode([
    {
      name         = "dashboard"
      image        = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/ord-lmnh-plants-dashboard:latest"
      cpu          = 0
      essential    = true
      portMappings = [
        {
          containerPort = 80
          hostPort      = 80
          protocol      = "tcp"
          appProtocol   = "http"
        },
        {
          containerPort = 8501
          hostPort      = 8501
          protocol      = "tcp"
          appProtocol   = "http"
        }
      ]
      environment = [
        {
          name  = "DB_PORT"
          value = "1433"
        },
        {
          name  = "AWS_KEY"
          value = var.AWS_KEY
        },
        {
          name  = "DB_USER"
          value = "beta"
        },
        {
          name  = "AWS_SKEY"
          value = var.AWS_SKEY
        },
        {
          name  = "DB_NAME"
          value = "plants"
        },
        {
          name  = "DB_HOST"
          value = "c10-plant-database.c57vkec7dkkx.eu-west-2.rds.amazonaws.com"
        },
        {
          name  = "DB_PASSWORD"
          value = "beta1"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/ord-lmnh-plants-dashboard"
          "awslogs-region"        = "eu-west-2"
          "awslogs-stream-prefix" = "ecs"
          "awslogs-create-group"  = "true"
        }
      }
    }
  ])

  runtime_platform {
    cpu_architecture     = "X86_64"
    operating_system_family = "LINUX"
  }
}
#This is the ecs needed for the long_term security_groups
