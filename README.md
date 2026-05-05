# personalWebsite

Source for [niv.schendel.me](https://niv.schendel.me) — a portfolio site with
an AI agent that argues for hiring Niv, plus a Python pipeline that builds
role-targeted CV variants from a shared facts source.

## Layout

- `apps/site/` — Astro 5 portfolio (deployed to GitHub Pages)
- `apps/chat-worker/` — Cloudflare Worker, AI agent backend
- `pipelines/resume/` — Python build pipeline for CV PDF variants
- `content/` — Single source of truth (facts.yaml, projects, agent brief, tone guide)
- `output/resumes/` — Generated PDFs (gitignored)
- `docs/superpowers/` — Specs and implementation plans

## Local dev

```bash
npm install
npm run dev:site    # http://localhost:4321
npm run dev:worker  # http://localhost:8787 (separate terminal)
```

## Stack

Astro 5 · React 18 · Cloudflare Workers · Anthropic SDK · GitHub Pages · Cloudflare DNS
