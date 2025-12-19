output "agent_id" {
    value = aws_bedrockagent_agent.main.agent_id
    description = "The Bedrock Agent ID"
}

output "agent_alias_id" {
    value = aws_bedrockagent_agent_alias.main.agent_alias_id
    description = "The Bedrock Agent Alias ID"
}
