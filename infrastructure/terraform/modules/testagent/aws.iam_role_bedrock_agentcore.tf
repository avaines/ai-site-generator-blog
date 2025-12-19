resource "aws_iam_role" "bedrock_agentcore" {
  assume_role_policy = data.aws_iam_policy_document.agentcore_trust.json
  name_prefix        = "AmazonBedrockExecutionRoleForAgents_"
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
    condition {
      test     = "StringEquals"
      values   = [var.aws["account_id"]]
      variable = "aws:SourceAccount"
    }
    condition {
      test     = "ArnLike"
      values   = ["arn:aws:bedrock-agentcore:${var.aws["region"]}:${var.aws["account_id"]}:agent/*"]
      variable = "AWS:SourceArn"
    }
  }
}

data "aws_iam_policy_document" "agentcore_permissions" {
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
}
