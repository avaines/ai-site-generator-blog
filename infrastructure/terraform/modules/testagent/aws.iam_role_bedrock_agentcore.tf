resource "aws_iam_role" "bedrock_agentcore" {
  name               = local.unique_id
  assume_role_policy = data.aws_iam_policy_document.agentcore_trust.json
}

resource "aws_iam_role_policy" "bedrock_agentcore" {
  policy = data.aws_iam_policy_document.agentcore_permissions.json
  role   = aws_iam_role.bedrock_agentcore.id
}

data "aws_iam_policy_document" "agentcore_trust" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      identifiers = ["bedrock-agentcore.amazonaws.com"]
      type        = "Service"
    }
  }
}

data "aws_iam_policy_document" "agentcore_permissions" {
  statement {
    effect = "Allow"
    actions = [
      "ecr:BatchGetImage",
      "ecr:GetAuthorizationToken",
      "ecr:GetDownloadUrlForLayer",
    ]

    resources = ["*"]
  }

  statement {
    effect = "Allow"
    actions = [
      "ecr:BatchGetImage",
      "ecr:GetDownloadUrlForLayer",
    ]

    resources = [
      aws_ecr_repository.main.arn
    ]
  }

  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
    ]

    resources = [
      "${module.s3_bucket.s3_bucket_arn}/*"
    ]
  }

  # CloudWatch Logs permissions for Bedrock AgentCore
  statement {
    effect = "Allow"
    actions = [
      "logs:DescribeLogStreams",
      "logs:CreateLogGroup"
    ]
    resources = [
      "${aws_cloudwatch_log_group.main.arn}/*"
    ]
  }

  statement {
    effect = "Allow"
    actions = ["logs:DescribeLogGroups"]
    resources = ["${aws_cloudwatch_log_group.main.arn}"]
  }

  statement {
    effect = "Allow"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "${aws_cloudwatch_log_group.main.arn}:*"
    ]
  }

  # X-Ray permissions
  statement {
    effect = "Allow"
    actions = [
      "xray:PutTraceSegments",
      "xray:PutTelemetryRecords",
      "xray:GetSamplingRules",
      "xray:GetSamplingTargets"
    ]
    resources = ["*"]
  }

  # CloudWatch metrics
  statement {
    effect = "Allow"
    actions = ["cloudwatch:PutMetricData"]
    resources = ["*"]
    condition {
      test     = "StringEquals"
      variable = "cloudwatch:namespace"
      values   = ["bedrock-agentcore"]
    }
  }

  # Bedrock model invocation
  statement {
    effect = "Allow"
    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream"
    ]
    resources = [
      "arn:aws:bedrock:*::foundation-model/*",
      "arn:aws:bedrock:${var.aws.region}:${var.aws.account_id}:*"
    ]
  }
}
