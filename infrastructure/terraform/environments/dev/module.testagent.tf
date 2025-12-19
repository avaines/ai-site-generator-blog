module "testagent" {
  source = "../../modules/testagent"

  aws = local.aws

  unique_ids = {
    local   = local.unique_id
    account = local.unique_id_account
    global  = local.unique_id_global
  }

  github_pat = aws_ssm_parameter.github_pat.value
}
