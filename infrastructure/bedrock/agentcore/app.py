"""
Bedrock AgentCore Application - Eleventy Static Site Generator

Function Call Flow:
               HTTP POST /invocations
                        │
                        ▼
             ┌──────────────────────┐
             │  invoke() [async]    │◄── @app.entrypoint
             └──────────────────────┘
                        │
           ┌────────────┴────────────┐
           │                         │
Returns immediately       Fires background task
           │                         │
           ▼                         ▼
   acknowledgment      asyncio.create_task()
   response                         │
                                    ▼
               ┌────────────────────────────────┐
               │ process_site_generation_async()│
               └────────────────────────────────┘
                            │
           ┌────────────────┼────────────────┐
           │                │                │
           ▼                ▼                ▼
┌──────────────────┐  ┌─────────────┐  ┌──────────────┐
│clone_repository()│  │generate_    │  │create_zip()  │
│                  │  │site_files_  │  │              │
│ - Clones GitHub  │  │async()      │  │ - Zip source │
│   repo with PAT  │  │             │  │   files      │
│ - Cleanup old    │  │ ┌─────────┐ │  │ - Upload to  │
│   clone          │  │ │agent.   │ │  │   S3 bucket  │
└──────────────────┘  │ │invoke_  │ │  │   (optional) │
                      │ │async()  │ │  │              │
                      │ │(3 tasks)│ │  │              │
                      │ └─────────┘ │  │ - Generate   │
                      │             │  │   presigned  │
                      │ - Structure │  │   URL        │
                      │ - Posts     │  │              │
                      │ - Theme     │  │ - Trigger    │
                      └─────────────┘  │   GitHub     │
                                       │   Action     │
                                       └──────────────┘

Architecture Notes:
- Async entrypoint returns immediately with acknowledgment
- Background processing uses asyncio tasks (not threads)
- Agent interactions use invoke_async() for proper async execution
- Zip file created and optionally uploaded to S3 for CI/CD pipeline
- After upload, generates presigned URL and triggers GHA for deployment
"""

import os
import shutil
import boto3
import asyncio
import zipfile
import requests

from pathlib import Path
from git import Repo
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands.models import BedrockModel
from strands_tools import file_read, file_write, editor, shell


app = BedrockAgentCoreApp()

os.environ["BYPASS_TOOL_CONSENT"] = "true"

repo_name = os.environ.get("GITHUB_REPO_NAME")
github_pat = os.environ.get("GITHUB_PAT")
github_pages_deploy_action_name = os.environ.get("GITHUB_DEPLOY_WF_NAME", "deploy.yml")


model = BedrockModel(
    # model_id="amazon.nova-pro-v1:0", # Use Amazon model for cost savings
    max_tokens=8096,
)

agent = Agent(
    model=model,
    tools=[file_read, file_write, editor, shell]
)


@app.entrypoint
async def invoke(payload):
    """Main entrypoint for generating Eleventy sites - async with background processing."""
    print(f"Agent has been called with {payload}")

    try:
        site_name = payload.get("site_name", "demo")
        user_prompt = payload.get("prompt", "Create a minimal Eleventy site.")
        posts_path = payload.get("posts_path")  # Path to posts in repo (e.g., "posts")

        # Optional params
        s3_bucket = payload.get("bucket")  # Optional
        theme_path = payload.get("theme_path")  # Optional path to theme files (e.g., "theme")

        # Return immediate acknowledgment
        acknowledgment = {
            "status": "accepted",
            "message": f"Site generation request received for '{site_name}'",
            "site_name": site_name,
            "prompt": user_prompt,
            "posts_path": posts_path,
            "theme_path": theme_path,
            "s3_bucket": s3_bucket,
            "note": "Processing in background. Check logs for completion status."
        }

        print(acknowledgment)

        # Start background task (fire and forget)
        asyncio.create_task(
            process_site_generation_async(site_name, user_prompt, posts_path, theme_path, s3_bucket)
        )

        return acknowledgment

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "type": type(e).__name__}


async def process_site_generation_async(site_name: str, user_prompt: str, posts_path: str, theme_path: str, s3_bucket: str):
    """Background async task to process site generation."""
    try:
        # Set up directories
        base_dir = Path(__file__).parent / "dist"
        repo_dir = base_dir / "repo"
        output_dir = base_dir / site_name
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output dir: {output_dir}")

        # Clone repository (use EnvVars for repo details)
        clone_repository(repo_dir)

        # Build paths to content in cloned repo
        posts_source_dir = repo_dir / posts_path if posts_path else None
        theme_source_dir = repo_dir / theme_path if theme_path else None

        # Generate files
        await generate_site_files_async(site_name, user_prompt, output_dir, posts_source_dir, theme_source_dir)

        # Create zip file and upload to S3 if bucket provided
        zip_path = create_zip(output_dir, site_name)

        if s3_bucket:
            s3_key, presigned_url = upload_zip_to_s3(zip_path, s3_bucket, site_name)
            print(f"Zip uploaded to: s3://{s3_bucket}/{s3_key}")
            print(f"Presigned URL: {presigned_url}")

            # Trigger GitHub Action with the presigned URL
            trigger_github_action(presigned_url, site_name)
        else:
            print(f"Zip created at: {zip_path}")

    except Exception as e:
        print(f"ERROR during background processing: {e}")
        import traceback
        traceback.print_exc()


# Helper Functions

def clone_repository(repo_dir: Path) -> Path:
    """Clone the GitHub repository specified in environment variables."""
    if not repo_name:
        raise ValueError("GITHUB_REPO_NAME environment variable is not set")
    if not github_pat:
        raise ValueError("GITHUB_PAT environment variable is not set")

    # Clean repo_dir if it exists
    if repo_dir.exists():
        shutil.rmtree(repo_dir)

    repo_dir.mkdir(parents=True, exist_ok=True)

    # Construct the authenticated URL
    # Format: https://<token>@github.com/<repo_name>.git
    repo_url = f"https://{github_pat}@github.com/{repo_name}.git"

    print(f"Cloning repository: {repo_name}")
    Repo.clone_from(repo_url, repo_dir)
    print(f"Repository cloned to: {repo_dir}")

    return repo_dir


def generate_site_files(site_name: str, user_prompt: str, output_dir: Path, posts_dir: Path = None, theme_dir: Path = None) -> int:
    """Generate site files using the agent - synchronous wrapper."""
    return asyncio.run(generate_site_files_async(site_name, user_prompt, output_dir, posts_dir, theme_dir))


async def generate_site_files_async(site_name: str, user_prompt: str, output_dir: Path, posts_dir: Path = None, theme_dir: Path = None) -> int:
    """Generate site files using the agent - broken into smaller focused tasks."""

    # Task 1: Generate basic 11ty structure (small, focused)
    print("Task 1: Generating base 11ty structure...")
    structure_prompt = f"""Create a minimal Eleventy (11ty) project structure in {output_dir}.

Requirements: {user_prompt}

Include:
- package.json with 11ty and basic dependencies
- .eleventy.js or eleventy.config.js configuration
- Basic directory structure (_includes, _layouts, etc.)

Keep it minimal - just the scaffold."""

    await agent.invoke_async(structure_prompt)
    print("Task 1: Base structure created")

    # Task 2: Integrate posts (if provided)
    if posts_dir and posts_dir.exists() and any(posts_dir.glob("*.md")):
        print(f"Task 2: Integrating posts from {posts_dir}...")
        posts_prompt = f"""Building on the existing 11ty project in {output_dir} (from the previous task), integrate posts from {posts_dir}.

Do the following:
1. Copy all non-draft Markdown files from {posts_dir} to {output_dir}/posts/ (create the directory if needed).
2. Update the 11ty config to parse these copied files as blog posts, including front-matter (title, date, tags, summary).
3. Set up collections, tags, and generate a home page, navigation, and sitemap based on the posts.
4. Ensure posts are excluded if front-matter has 'draft: true'.

Only handle posts—don't regenerate the base structure."""

        await agent.invoke_async(posts_prompt)
        print("Task 2: Posts integrated")

    # Task 3: Apply theme (if provided)
    if theme_dir and theme_dir.exists():
        print(f"Task 3: Applying theme from {theme_dir}...")
        theme_prompt = f"""Building on the existing 11ty project in {output_dir} (including any posts from the previous task), apply the theme from {theme_dir}.

Do the following:
1. Copy layout.html from {theme_dir} to {output_dir}/_layouts/ (create if needed).
2. Copy styles.css from {theme_dir} to {output_dir}/_includes/ or integrate it appropriately.
3. Copy any partials from {theme_dir}/partials/ to {output_dir}/_includes/partials/.
4. Update the 11ty config and layouts to use these files (e.g., reference {{layout}} in posts).
5. If any files are missing, log a warning but proceed.

Only apply the theme—don't regenerate posts or structure."""

        await agent.invoke_async(theme_prompt)
        print("Task 3: Theme applied")

    # Count created files
    all_files = list(output_dir.rglob("*"))
    num_files = len([f for f in all_files if f.is_file()])

    if num_files == 0:
        raise ValueError("No files were created.")

    print("Task 4: Validation.")
    validation_prompt = f"""Review the complete 11ty project in {output_dir}.

Please:
1. Verify package.json dependencies and config files (.eleventy.js) are correct.
2. Check that posts were copied to {output_dir}/posts/ and are parseable (no drafts included).
3. Confirm theme files (layout.html, styles.css, partials) were copied and integrated.
4. Test for broken paths, syntax errors, or missing files—fix any you find immediately using available tools.
5. If issues persist, report them clearly.

Confirm the project is ready to build."""

    await agent.invoke_async(validation_prompt)
    print("Task 4: Validation completed")

    print(f"Total files created: {num_files} tokens used during generation.")
    return num_files


def create_zip(output_dir: Path, site_name: str) -> Path:
    """Create a zip file of the generated site."""
    zip_path = output_dir.parent / f"{site_name}.zip"

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in output_dir.rglob("*"):
            if file_path.is_file():
                 # Exclude node_modules directories
                if "node_modules" in file_path.parts:
                    continue

                tmp_name = file_path.relative_to(output_dir) # Add file to zip with relative path
                zipf.write(file_path, tmp_name)

    print(f"Created zip: {zip_path}")
    return zip_path


def upload_zip_to_s3(zip_path: Path, bucket: str, site_name: str) -> tuple[str, str]:
    """Upload zip file to S3 and return the S3 key and presigned URL."""
    s3_client = boto3.client('s3')
    s3_key = f"{site_name}/{zip_path.name}"

    s3_client.upload_file(
        str(zip_path),
        bucket,
        s3_key,
        ExtraArgs={'ContentType': 'application/zip'}
    )

    # Generate presigned URL (expires in 1 hour)
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': s3_key},
        ExpiresIn=3600  # 1 hour
    )

    return s3_key, presigned_url


def trigger_github_action(presigned_url: str, site_name: str):
    """Trigger a GitHub Action workflow dispatch with the presigned URL."""

    if not repo_name or not github_pat:
        raise ValueError("GITHUB_REPO_NAME and GITHUB_PAT environment variables must be set")

    # GitHub API URL for workflow dispatch
    url = f"https://api.github.com/repos/{repo_name}/actions/workflows/{github_pages_deploy_action_name}/dispatches"

    headers = {
        "Authorization": f"token {github_pat}",
        "Accept": "application/vnd.github.v3+json"
    }

    payload = {
        "ref": "main",
        "inputs": {
            "presigned_url": presigned_url,
            "site_name": site_name
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()

    print(f"GitHub Action triggered successfully for site '{site_name}' with presigned URL.")

if __name__ == "__main__":
    PORT = 8080
    app.run(port=PORT)
