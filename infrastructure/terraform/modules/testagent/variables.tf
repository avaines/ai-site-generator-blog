##
# Generic tfscaffold Module Variables
##

variable "aws" {
  type = object({
    account_id   = string
    default_tags = optional(map(string), {})
    region       = string
  })
}

variable "module_parents" {
  type        = list(string)
  description = "List of parent module names"
  default     = []
}

variable "unique_ids" {
  type = object({
    # All marked as optional for consistency of code.
    # Whether each is optional depends on the module implementation.
    local   = optional(string, null)
    account = optional(string, null)
    global  = optional(string, null)
  })
}

variable "default_tags" {
  type        = map(string)
  description = "A map of default tags to apply to all taggable resources within the component"
  default     = {}
}

##
# Variables specific to this Module
##

variable "github_pat" {
  type        = string
  description = "GitHub PAT token for accessing private repositories"
}

variable "bedrock_foundation_model_arn" {
  type        = string
  description = "The ARN of the Bedrock Foundation Model to use"
}

variable "bedrock_embedding_model_arn" {
  type        = string
  description = "The ARN of the Bedrock Embedding Model to use for the knowledge base"
}
