# Infrastructure — dev env deployment

How to deploy the `dev` Terraform environment - basically just the AgentCore Bedrock service and the container running the agent.

## Prereqs

- Terraform (check `versions.tf` files).
- Docker running locally (the module currently builds the container image locally and pushes to ECR).
- AWS credentials configured (e.g. `AWS_PROFILE` or environment variables) with permissions to create ECR, IAM, and Bedrock resources.

## Deploy (local machine with Docker)
1. CD into the `dev` environment folder:

```bash
cd infrastructure/terraform/environments/dev
```

2. Initialize Terraform (downloads providers and modules):

```bash
terraform init
```

3. Review the plan and apply any changes

```bash
terraform plan
terraform apply
```

- To check the pushed image resource in state

```bash
terraform state list | grep testagent
terraform state show module.testagent.docker_registry_image.agentcore
```

- Or use the AWS CLI

```bash
aws ecr describe-repositories --repository-names testagent
```

## Notes

- The module currently builds the Docker image from the repository path `infrastructure/bedrock/agentcore` by default. Make sure Docker is running and that the build context exists relative to the module.
