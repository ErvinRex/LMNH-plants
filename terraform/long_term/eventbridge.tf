# Eventbridge trigger for upload-wipe-pipeline

resource "aws_security_group" "ecs-sec-group" {
  name   = "ord-lmnh-ecs-sg"
  description = "Allow traffic through ECS task"
  vpc_id = data.aws_vpc.cohort-10-vpc.id

  ingress {
        cidr_blocks       = ["0.0.0.0/0"]
        from_port         = 80
        protocol          = "tcp"
        to_port           = 80
    }
}

resource "aws_iam_role_policy" "ecs_policy" {
  name = "ord-lmnh-ecs-policy"
  role = aws_iam_role.ecs_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "ecs:RunTask"
        ],
        Resource = "*",
        Effect = "Allow"
      }
    ]
  })
}

resource "aws_iam_role" "ecs_execution_role" {
  name               = "ord-lmnh-ecsTaskExecutionRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "scheduler.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      },
    ]
  })
}

resource "aws_scheduler_schedule" "pipeline_schedule" {
  name       = "ord-lmnh-upload-wipe-pipeline-schedule"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 0 * * ? *)"

  target {
    arn      = data.aws_ecs_cluster.c10-ecs-cluster.arn
    role_arn = aws_iam_role.ecs_execution_role.arn
    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.pipeline-task-def.arn
      launch_type = "FARGATE"
      network_configuration {
        subnets = ["subnet-0f1bc89d0670672b5", "subnet-010c8f9ace38ac103", "subnet-05a01546985e339a6"]
        assign_public_ip = true
        security_groups = [aws_security_group.ecs-sec-group.id]
      }
    }
  }
}