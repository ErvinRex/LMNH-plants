# This terraforms a CloudWatch notification which triggers the health_check function

resource "aws_lambda_permission" "allow_event_bridge_health_check" {
  statement_id  = "AllowExecutionFromEventBridgeHealthCheck"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.health_check_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.health_check_event_rule.arn
}

resource "aws_cloudwatch_event_rule" "health_check_event_rule" {
  name                = "health_check_event_rule"
  description         = "Triggers every hour"
  schedule_expression = "cron(0 * * * ? *)"
}

resource "aws_cloudwatch_event_target" "health_check_lambda_target" {
  rule      = aws_cloudwatch_event_rule.health_check_event_rule.name
  target_id = "HealthCheckLambdaTarget"
  arn       = aws_lambda_function.health_check_lambda.arn

  input_transformer {
    input_paths = {
      "time" = "$.time"
    }
    input_template = "\"Time of triggering: <time>\""
  }
}

# This is the second resource needed for the pipeline

resource "aws_lambda_permission" "allow_event_bridge_pipeline" {
  statement_id  = "AllowExecutionFromEventBridgePipeline"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.pipeline_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.pipeline_event_rule.arn
}

resource "aws_cloudwatch_event_rule" "pipeline_event_rule" {
  name                = "pipeline_event_rule"
  description         = "Triggers every hour"
  schedule_expression = "cron(* * * * ? *)"
}

resource "aws_cloudwatch_event_target" "pipeline_lambda_target" {
  rule      = aws_cloudwatch_event_rule.pipeline_event_rule.name
  target_id = "PipelineLambdaTarget"
  arn       = aws_lambda_function.pipeline_lambda.arn

  input_transformer {
    input_paths = {
      "time" = "$.time"
    }
    input_template = "\"Time of triggering: <time>\""
  }
}

# Configuration for the ECS security group and task execution role

resource "aws_security_group" "ecs_sec_group" {
  name        = "ecs_sec_group"
  description = "Allow traffic through ECS task"
  vpc_id      = "vpc-0c4f01396d92e1cc7"

  ingress {
    cidr_blocks = ["0.0.0.0/0"]
    from_port   = 80
    protocol    = "tcp"
    to_port     = 80
  }
}

resource "aws_iam_role" "ecs_execution_role" {
  name = "ecs_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      },
    ]
  })
}

resource "aws_iam_role_policy" "ecs_policy" {
  name = "ecs_policy"
  role = aws_iam_role.ecs_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = ["ecs:RunTask"],
        Resource = "*",
        Effect = "Allow"
      },
    ]
  })
}

# Scheduler configuration for ECS task execution

resource "aws_scheduler_schedule" "upload_wipe_pipeline_schedule" {
  name = "upload_wipe_pipeline_schedule"

  flexible_time_window {
    mode = "OFF"
  }

  schedule_expression = "cron(0 0 * * ? *)"

  target {
    arn      = data.aws_ecs_cluster.c10_ecs_cluster.arn
    role_arn = aws_iam_role.ecs_execution_role.arn
    ecs_parameters {
      task_definition_arn = aws_ecs_task_definition.pipeline_task_def.arn
      launch_type = "FARGATE"
      network_configuration {
        subnets = ["subnet-0f1bc89d0670672b5", "subnet-010c8f9ace38ac103", "subnet-05a01546985e339a6"]
        assign_public_ip = true
        security_groups = [aws_security_group.ecs_sec_group.id]
      }
    }
  }
}
