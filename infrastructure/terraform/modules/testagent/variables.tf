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

## Image / build variables
variable "image_name" {
  type        = string
  description = "Name of the image / ECR repository to create. If empty the module unique id will be used."
  default     = ""
}

variable "image_tag" {
  type        = string
  description = "Tag to apply to the built image"
  default     = "latest"
}

variable "build_context_rel_path" {
  type        = string
  description = "Path to the Docker build context relative to this module (e.g. ../../../bedrock/agentcore)"
  default     = "../../../bedrock/agentcore"
}
