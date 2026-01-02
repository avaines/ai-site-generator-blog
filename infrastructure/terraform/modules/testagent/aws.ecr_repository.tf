data "aws_ecr_authorization_token" "auth" {}

resource "aws_ecr_repository" "main" {
  name = local.unique_id

  force_delete         = true
  image_tag_mutability = "MUTABLE"

  tags = local.default_tags
}
