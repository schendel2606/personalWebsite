# personalWebsite

Source for [niv.schendel.me](https://niv.schendel.me) — a portfolio site with
an AI agent that argues for hiring Niv, plus a Python pipeline that builds
role-targeted CV variants from a shared facts source.

## Live URLs

| URL | What it serves |
|---|---|
| <https://niv.schendel.me> | The portfolio (canonical) |
| <https://schendel.me>, <https://www.schendel.me> | 301 redirect to the canonical |
| <https://chat.niv.schendel.me> | Chat API (the AI recruiter agent) |

## Layout

- `apps/site/` — Astro portfolio (deployed to GitHub Pages)
- `apps/chat-worker/` — Cloudflare Worker; serves the chat API at `chat.niv` and the apex/www redirects
- `pipelines/resume/` — Python build pipeline for CV PDF variants
- `content/` — Single source of truth (facts.yaml, projects, agent brief, tone guide)
- `output/resumes/` — Generated PDFs (gitignored)
- `docs/superpowers/` — Specs and implementation plans
- `docs/SETUP.md` — One-time production setup checklist

## Local dev

```bash
npm install
npm run dev:site    # http://localhost:4321
npm run dev:worker  # http://localhost:8787 (separate terminal)
```

For the worker, copy `apps/chat-worker/.dev.vars.example` to `apps/chat-worker/.dev.vars` and fill in `ANTHROPIC_API_KEY` and `SESSION_COOKIE_SECRET`. Set `COOKIE_DOMAIN=localhost` in the same file so cookies work over HTTP locally.

## Stack

Astro · React · TypeScript · Cloudflare Workers + KV · Anthropic SDK (`claude-haiku-4-5`) · GitHub Pages · Cloudflare DNS · Vitest · Wrangler
