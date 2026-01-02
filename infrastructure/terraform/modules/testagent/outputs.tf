output "agent_runtime_id" {
  description = "The Bedrock AgentCore Runtime ID"
  value       = aws_bedrockagentcore_agent_runtime.main.agent_runtime_id
}
