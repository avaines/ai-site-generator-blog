variable "aws_account_id" {
  type        = string
  description = "AWS Account IDs for the account that will be used by providers"
}

variable "region" {
  type        = string
  description = "The AWS Region"
}

variable "environment" {
  type        = string
  description = "The environment variables are being inherited from"
}

variable "default_tags" {
  type        = map(string)
  description = "A map of default tags to apply to all taggable resources within the component"
  default     = {}
}

##
# Variables specific to this Component
##

variable "initial_cli_secrets_provision_override" {
  type        = map(string)
  description = "A map of default value to intialise SSM secret values with. Only useful for initial setup of the account due to lifecycle rules."
  default     = {}
  # Usage like:
  #  make terraform-apply opts="-var initial_cli_secrets_provision_override={\"github_pat\":\"l0ngstr1ng\"}"
}
