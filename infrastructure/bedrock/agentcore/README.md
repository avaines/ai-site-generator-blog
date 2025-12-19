# Eleventy Site Generator Agent

AI-powered static site generator using AWS Bedrock AgentCore and Strands Agent SDK. Clones content from GitHub repositories, generates Eleventy (11ty) source projects from natural language prompts, and creates deployable zip files for CI/CD pipelines.

## What it does

- Clones a GitHub repository containing your content (posts, theme files)
- Accepts a prompt and generates a complete Eleventy static site source around your content
- Uses a 3-task approach for efficient token usage (structure → posts → theme)
- Integrates existing posts and optional theme files into the generated site
- Creates structured file output (package.json, configs, templates, CSS)
- Packages source files into a zip for CI/CD pipeline consumption
- Optionally uploads zip to S3 for downstream build processes
- Async processing - returns immediately while generation happens in background

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

### Environment Variables

Set these environment variables before running:

```bash
export GITHUB_REPO_NAME="owner/repository"  # e.g., "avaines/author-driven-development-blog"
export GITHUB_PAT="your_personal_access_token"  # GitHub Personal Access Token with repo read access
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

Generate a site with content from GitHub (basic):
```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "site_name": "my-blog",
    "prompt": "A modern blog site with dark theme",
    "posts_path": "posts"
  }'
```

Generate a site with posts and theme files:
```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "site_name": "my-blog",
    "prompt": "A modern blog site",
    "posts_path": "posts",
    "theme_path": "theme"
  }'
```

Generate and upload to S3:
```bash
curl -X POST http://localhost:8080/invocations \
  -H "Content-Type: application/json" \
  -d '{
    "site_name": "my-blog",
    "prompt": "A blog about technology",
    "posts_path": "posts",
    "theme_path": "theme",
    "bucket": "my-site-dumps"
  }'
```

### API Payload Schema

```json
{
  "site_name": "string (optional, default: 'demo')",
  "prompt": "string (optional, default: 'Create a minimal Eleventy site.')",
  "posts_path": "string (optional) - Path to posts directory in the repo (e.g., 'posts')",
  "theme_path": "string (optional) - Path to theme files in the repo (e.g., 'theme')",
  "bucket": "string (optional) - S3 bucket name for static site hosting"
}
```

### Response

The API returns immediately with an acknowledgment while processing happens in the background:

```json
{
  "status": "accepted",
  "message": "Site generation request received for 'my-blog'",
  "site_name": "my-blog",
  "prompt": "A modern blog site",
  "posts_path": "posts",
  "theme_path": "theme",
  "s3_bucket": "my-site-dumps",
  "note": "Processing in background. Check logs for completion status."
}
```

### Docker

```bash
docker build -t agentcore-local .
docker run --rm -p 8080:8080 \
  -e GITHUB_REPO_NAME="owner/repository" \
  -e GITHUB_PAT="your_pat_token" \
  agentcore-local
```

## Output

Generated site source files: `./dist/{site_name}/`
Zip file: `./dist/{site_name}.zip`
Cloned repository: `./dist/repo/`

If S3 bucket is provided, zip file is uploaded to: `s3://{bucket}/{site_name}/{site_name}.zip`

**Note**: The zip contains Eleventy source files, not built HTML. Your CI/CD pipeline should extract the zip, run `npm install`, then `npm run build` to generate the static site.

## How it Works

1. **Accept Request**: API immediately returns acknowledgment and starts background task
2. **Clone Repository**: Clones the GitHub repository specified in `GITHUB_REPO_NAME` using `GITHUB_PAT` for authentication
3. **Build Paths**: Constructs paths to posts and theme directories in the cloned repo based on API payload
4. **Generate Site** (3-task approach for token efficiency):
   - **Task 1**: Generate base 11ty structure (package.json, config, directories)
   - **Task 2**: Integrate posts from repository (if provided)
   - **Task 3**: Apply theme files (if provided)
5. **Create Zip**: Package all source files into a zip file
6. **Upload to S3** (optional): Upload zip file to S3 for CI/CD pipeline to extract and build

## TODO

### Infrastructure & Deployment
- [x] Git Integration: Clone repository and use content
- [x] Support for posts and theme files from repository
- [ ] Terraform for AWS deployment (Lambda, API Gateway, S3, IAM)
- [ ] CI/CD pipelines for building and deploying to AWS
- [ ] Environment-specific configurations (dev, staging, prod)
- [ ] Secrets Manager integration for GitHub PAT

### Invoke Mechanisms
- [ ] EventBridge trigger for scheduled regeneration
- [ ] S3 event trigger (on config file update)
- [ ] API Gateway webhook for manual invocations
- [ ] GitHub Actions integration for CI/CD triggers
