resource "docker_registry_image" "main" {
  name          = docker_image.main.name
  keep_remotely = true

  auth_config {
    address  = data.aws_ecr_authorization_token.auth.proxy_endpoint
    username = "AWS"

    # authorization_token decodes to "AWS:<token>", so split and take the second part
    password = split(":", base64decode(data.aws_ecr_authorization_token.auth.authorization_token))[1]
  }
}

resource "docker_image" "main" {
  name = "${aws_ecr_repository.main.repository_url}:${var.image_tag}"

  build {
    context    = "${path.module}/${var.build_context_rel_path}"
    dockerfile = "Dockerfile"
    platform   = "arm64"
  }
}
