resource "aws_bedrockagentcore_agent_runtime" "main" {
  agent_runtime_name = replace(local.unique_id, "-", "_")

  role_arn = aws_iam_role.bedrock_agentcore.arn

  environment_variables = {
    GITHUB_REPO_NAME = "avaines/ai-site-generator-blog"
    GITHUB_PAT       = var.github_pat
  }

  agent_runtime_artifact {
    container_configuration {
      container_uri = "${aws_ecr_repository.main.repository_url}:latest"
    }
  }

  network_configuration {
    network_mode = "PUBLIC"
  }

  depends_on = [
    docker_registry_image.main
  ]
}
