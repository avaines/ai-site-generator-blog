# Agents Contract

## Editor‑In‑Chief (Human)

Goal: Write and approve posts. Tone and direction.
Inputs: Markdown in `posts/`.
Outputs: Published posts.
Constraints: UK English; first person; code with language fences.

## Site Synthesiser (AI)

Goal: Generate a static site from human content and the contract.
Inputs: `SITE_CONTRACT.md`, directory listing, posts, optional `theme/`.
Outputs: HTML+CSS in `/dist` (index, posts, tags, feed optional).
Constraints: Deterministic routing; no external network calls.

## Navigator (AI)

Goal: Build navigation, sitemap, and optional feed.
Inputs: Parsed front‑matter and headings.
Outputs: `nav.html`, `sitemap.xml`, optional `feed.xml`.
Constraints: Do not invent content.

## Lint & Link Checker (AI‑assisted)

Goal: Validate front‑matter, links, alt text, code fences.
Outputs: `dist/lint-report.json` and non‑zero exit on hard failures.

# Site Contract

- Posts live in `posts/` with front‑matter: `title`, `date` (ISO), `tags`, `summary`, optional `draft`.
- Logos live in `assets/logos/` (prefer `logo.svg` + `favicon.png`).
- Images live in `assets/images/` and are referenced relatively.
- If `theme/layout.html` exists, use it with tokens: `{{title}}`, `{{content}}`, `{{site_title}}`, `{{nav}}`.
- Output goes to `dist/` with clean URLs (`/yyyy/mm/slug/`).
- Generate: home page, per‑post pages, tag pages, `sitemap.xml`, optional Atom `feed.xml`.
- Accessibility first; minimal or no JavaScript.
