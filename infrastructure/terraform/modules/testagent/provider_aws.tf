provider "aws" {
  region = var.aws["region"]

  default_tags {
    tags = local.default_tags
  }
}
