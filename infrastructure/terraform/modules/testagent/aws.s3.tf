module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = local.unique_id_global
  acl    = "private"

  force_destroy            = true
  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  versioning = {
    enabled = true
  }
}
