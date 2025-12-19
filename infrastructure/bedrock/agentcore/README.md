# Eleventy Site Generator Agent

AI-powered static site generator using AWS Bedrock AgentCore and Strands Agent SDK. Generates Eleventy (11ty) projects from natural language prompts, packages them as zip files, and optionally uploads to S3 with presigned URLs.

## What it does

- Accepts a prompt and generates a complete Eleventy static site
- Creates structured file output (HTML, CSS, JS, configs)
- Packages the site as a downloadable zip
- Optionally uploads to S3 and returns a presigned URL (1 hour expiry)

## References

- https://aws.plainenglish.io/getting-started-with-bedrock-agentcore-runtime-3eaae1f517cc
- https://github.com/awslabs/amazon-bedrock-agentcore-samples/tree/main/02-use-cases
- https://strandsagents.com/latest/documentation/docs/examples/python/file_operations/

## Local Development

### Setup

```bash
pyenv virtualenv 3.13 agentcore-test
pyenv activate agentcore-test
pip install -r requirements.txt
```

### Run locally

```bash
python app.py
# Server starts on http://localhost:8080
```

### Test the API

Health check:
```bash
curl http://localhost:8080/ping
# {"status":"Healthy","time_of_last_update":1765922327}
```

Generate a site (local only):
```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"site_name": "demo-11ty", "prompt": "A minimal site with a disco theme"}'
```

Generate and upload to S3:
```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{"site_name": "my-site", "prompt": "A blog about cats", "s3_bucket": "my-site-dumps"}'
```

### Docker

```bash
docker build -t agentcore-local .
docker run --rm -p 8080:8080 agentcore-local
```

## Output

Generated sites are saved to: `./dist/{site_name}/`
Zip files are created at: `./dist/{site_name}.zip`

## TODO

### Infrastructure & Deployment
- [ ] Terraform for AWS deployment (Lambda, API Gateway, S3, IAM)
- [ ] CI/CD pipelines for building and deploying to AWS
- [ ] Environment-specific configurations (dev, staging, prod)

### Git Integration (Primary Goal)
- [ ] Clone git repository containing site configuration
- [ ] Read prompt/config from repo
- [ ] Generate site based on repo's stored prompt/requirements
- [ ] Zip and upload generated site

### Invoke Mechanisms
- [ ] EventBridge trigger for scheduled regeneration
- [ ] S3 event trigger (on config file update)
- [ ] API Gateway webhook for manual invocations
- [ ] GitHub Actions integration for CI/CD triggers
