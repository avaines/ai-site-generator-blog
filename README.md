# Author‑Driven Development (ADD)

Writing code is inhuman

*If you can't be bothered to write it, why should anyone read it; lets leave the creativity to humans but lets leave the code to robots and big nerds.*

## Concept
Human‑written posts; AI assembles the site around them, we don't really care about the website, thats nerd stuff leave it to the robots.

Each run reads `SITE_CONTRACT.md` and emits static HTML to `./dist` by way of the instructions in `AGENTS.MD`. The AI is mostly left to make all the tech decisions and what the site is going to look like........ hopefully it works every time, and can be navigated.

Will it work? Will it be accessibile? Will it be responsive? Why would you do this? <- All questions asked by AI Skeptics

## Quick Start

1. Write a post in `posts/`.
2. Set secrets: `OPENAI_API_KEY`, `MODEL`.
3. `npm i` (once), then `node scripts/build.mjs`.
4. ????
5. AI
