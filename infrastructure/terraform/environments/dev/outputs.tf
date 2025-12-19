output "agent_id" {
  value       = module.testagent.agent_id
  description = "The Bedrock Agent ID"
}

output "agent_alias_id" {
  value       = module.testagent.agent_alias_id
  description = "The Bedrock Agent Alias ID"
}
