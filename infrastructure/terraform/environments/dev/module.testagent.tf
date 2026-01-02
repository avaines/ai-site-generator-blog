module "testagent" {
  source = "../../modules/testagent"

  aws = local.aws

  unique_ids = {
    local   = "${local.unique_id}-testagent"
    account = "${local.unique_id_account}-testagent"
    global  = "${local.unique_id_global}-testagent"
  }

  default_tags   = local.default_tags
  module_parents = ["dev"]
  github_pat     = aws_ssm_parameter.github_pat.value
}
