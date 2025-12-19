terraform {
  backend "s3" {
    bucket       = "804221019544-tfstate"
    key          = "state/dev/terraform.tfstate"
    region       = "us-east-1"
    use_lockfile = true
  }
}
