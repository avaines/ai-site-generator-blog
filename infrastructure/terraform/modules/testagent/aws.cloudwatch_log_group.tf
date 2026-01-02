resource "aws_cloudwatch_log_group" "main" {
  name = "/aws/bedrock-agentcore/runtimes/${aws_bedrockagentcore_agent_runtime.main.agent_runtime_id}-DEFAULT"
}
