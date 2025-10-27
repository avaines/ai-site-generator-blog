#!/usr/bin/env node
// Ensure all posts have proper front-matter

import fs from "node:fs/promises";
import path from "node:path";

const postsDir = path.join(process.cwd(), "posts");

try {
  const files = await fs.readdir(postsDir);
  const mdFiles = files.filter(f => f.endsWith(".md"));
  const errors = [];

  console.log(`Checking ${mdFiles.length} posts...`);

  for (const file of mdFiles) {
    const filePath = path.join(postsDir, file);
    const content = await fs.readFile(filePath, "utf8");

    // Check for front-matter block
    const frontMatterMatch = content.match(/^---\s*\n([\s\S]*?)\n---/);
    if (!frontMatterMatch) {
      errors.push(`${file}: No front-matter found`);
      continue;
    }

    const frontMatter = frontMatterMatch[1];

    // Check required fields
    const requiredFields = {
      title: /title:\s*["']?.+["']?/,
      date: /date:\s*["']?\d{4}-\d{2}-\d{2}["']?/,
      tags: /tags:\s*\[.+\]/,
      summary: /summary:\s*["'].+["']/
    };

    const missing = [];
    for (const [field, regex] of Object.entries(requiredFields)) {
      if (!regex.test(frontMatter)) {
        missing.push(field);
      }
    }

    if (missing.length > 0) {
      errors.push(`${file}: Missing or invalid fields: ${missing.join(", ")}`);
    } else {
      console.log(`${file}: Valid`);
    }
  }

  if (errors.length > 0) {
    console.log("\nValidation errors:");
    errors.forEach(error => console.log(error));
    process.exit(1);
  } else {
    console.log(`\nAll ${mdFiles.length} posts validated successfully!`);
  }

} catch (error) {
  console.error("Validation failed:", error.message);
  process.exit(1);
}
