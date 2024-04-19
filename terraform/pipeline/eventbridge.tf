resource "aws_lambda_permission" "allow_event_bridge" {
  statement_id  = "AllowExecutionFromEventBridge"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ord-lmnh-pipeline-terraform.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.ord-lmnh-pipeline-terraform.arn
}

resource "aws_cloudwatch_event_rule" "ord-lmnh-pipeline-terraform" {
  name                = "ord-lmnh-pipeline-terraform"
  description         = "Triggers every hour"
  schedule_expression = "cron(* * * * ? *)"
}

resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.ord-lmnh-pipeline-terraform.name
  target_id = "MyLambdaFunctionTarget"
  arn       = aws_lambda_function.ord-lmnh-pipeline-terraform.arn

  input_transformer {
    input_paths = {
      "time" = "$.time"
    }
    input_template = "\"Time of triggering: <time>\""
  }
}
