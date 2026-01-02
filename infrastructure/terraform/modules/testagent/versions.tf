terraform {
  required_providers {
    aws = {
      source = "hashicorp/aws"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 3.6"
    }
  }
}
