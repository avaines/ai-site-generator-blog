import os
import boto3
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from bedrock_agentcore import BedrockAgentCoreApp
from strands import Agent
from strands_tools import file_read, file_write, editor

app = BedrockAgentCoreApp()

os.environ["BYPASS_TOOL_CONSENT"] = "true"
agent = Agent(tools=[file_read, file_write, editor])


def generate_site_files(site_name: str, user_prompt: str, output_dir: Path) -> int:
    """Generate site files using the agent."""
    prompt = f"""Generate an Eleventy (11ty) project.
Project name: {site_name}
Requirements: {user_prompt}

Create a minimal Eleventy static site generator project structure under the {output_dir} directory.

Return JSON with a 'files' array. Each file has 'path' and 'content'."""

    agent(prompt)

    # Count created files
    all_files = list(output_dir.rglob("*"))
    num_files = len([f for f in all_files if f.is_file()])

    if num_files == 0:
        raise ValueError("No files were created.")

    print(f"Total files created: {num_files}")

    # Validation phase: ask agent to verify the generated code
    validation_prompt = f"""Review the Eleventy project you just created in {output_dir}.

Please:
1. Read the package.json file to verify all dependencies are correct
2. Check that all referenced files and paths exist
3. Verify the configuration files (.eleventy.js or eleventy.config.js) are syntactically valid
4. Look for any obvious issues like missing files, broken references, or syntax errors
5. If you find any problems, fix them immediately

After reviewing, confirm the project is working or report what you fixed."""

    agent(validation_prompt)
    print("Code validation completed")

    return num_files


def create_zip(output_dir: Path, site_name: str) -> Path:
    """Create a zip file from the output directory."""
    zip_path = output_dir.parent / f"{site_name}.zip"

    with ZipFile(zip_path, "w", ZIP_DEFLATED) as z:
        for p in output_dir.rglob("*"):
            if p.is_file():
                arcname = p.relative_to(output_dir)
                z.write(p, arcname)
                print(f"Added to zip: {arcname}")

    print(f"Created zip: {zip_path}")
    return zip_path


def upload_to_s3(zip_path: Path, bucket: str, site_name: str) -> str:
    """Upload zip to S3 and return presigned URL."""
    s3_client = boto3.client('s3')
    s3_key = f"sites/{site_name}.zip"

    # Upload file
    s3_client.upload_file(str(zip_path), bucket, s3_key)
    print(f"Uploaded to s3://{bucket}/{s3_key}")

    # Generate presigned URL (valid for 1 hour)
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket, 'Key': s3_key},
        ExpiresIn=3600
    )

    return presigned_url


@app.entrypoint
def invoke(payload):
    """Main entrypoint for generating Eleventy sites."""
    print(f"Agent has been called with {payload}")

    try:
        site_name = payload.get("site_name", "demo")
        user_prompt = payload.get("prompt", "Create a minimal Eleventy site.")
        s3_bucket = payload.get("bucket")  # Optional

        output_dir = Path(__file__).parent / "dist" / site_name
        output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Output dir: {output_dir}")

        # Generate files
        generate_site_files(site_name, user_prompt, output_dir)

        # Create zip
        zip_path = create_zip(output_dir, site_name)

        result = {
            "status": "ok",
            "site_name": site_name,
            "project_dir": str(output_dir.absolute()),
            "zip_path": str(zip_path.absolute())
        }

        # Upload to S3 if bucket provided
        if s3_bucket:
            presigned_url = upload_to_s3(zip_path, s3_bucket, site_name)
            result["s3_url"] = presigned_url
            result["s3_bucket"] = s3_bucket

        print(result)
        return result

    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {"error": str(e), "type": type(e).__name__}


if __name__ == "__main__":
    PORT = 8080
    app.run(port=PORT)
