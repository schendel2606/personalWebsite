# Production Setup

One-time steps to bring `niv.schendel.me` and `chat.niv.schendel.me` live.

> **Important — order matters.** Complete steps 1, 2, and 6 (KV namespace + worker secrets + GitHub Actions secret) **before** the first push to `main`. The CI workflows trigger on push and will fail noisily if any of those are missing or if `wrangler.toml` still contains the placeholder KV id. Suggested order: do all 7 setup steps locally on a feature branch, then merge to `main` to trigger the first deploy.

## 1. Cloudflare KV namespace

```bash
cd apps/chat-worker
npx wrangler login
npx wrangler kv:namespace create RATE_LIMIT_KV
```

Copy the returned `id` and replace `PLACEHOLDER_BIND_VIA_WRANGLER_KV_CREATE`
in `apps/chat-worker/wrangler.toml`.

Commit the wrangler.toml update.

## 2. Cloudflare Worker secrets

```bash
cd apps/chat-worker
npx wrangler secret put ANTHROPIC_API_KEY
# paste your sk-ant-api03-... key when prompted

# Generate a 64-char hex secret for cookie signing
openssl rand -hex 32
npx wrangler secret put SESSION_COOKIE_SECRET
# paste the generated value
```

## 3. Cloudflare DNS

In the Cloudflare dashboard for `schendel.me`:

- Add CNAME for `niv` (the apex of niv.schendel.me):
  - Type: CNAME
  - Name: `niv`
  - Target: `schendel2606.github.io`
  - Proxy status: **DNS only** (gray cloud)

- Add a CNAME for the chat subdomain:
  - Type: CNAME
  - Name: `chat.niv`
  - Target: (auto-resolved when wrangler routes are configured below)
  - Proxy status: **Proxied** (orange cloud)

## 4. Cloudflare Worker route

In `apps/chat-worker/wrangler.toml`, add:

```toml
[[routes]]
pattern = "chat.niv.schendel.me/*"
zone_name = "schendel.me"
```

Then deploy:

```bash
cd apps/chat-worker && npx wrangler deploy
```

## 5. GitHub Pages config

In repo settings -> Pages:
- Source: GitHub Actions
- Custom domain: `niv.schendel.me`
- Wait for the DNS check to pass (may take a few minutes)
- Enable "Enforce HTTPS" once available

## 6. GitHub Actions secret

In repo settings -> Secrets and variables -> Actions:
- Add: `CLOUDFLARE_API_TOKEN`
- Generate the token at https://dash.cloudflare.com/profile/api-tokens
  with permissions: Account -> Workers Scripts -> Edit, Zone -> DNS -> Edit

## 7. Repo visibility

In repo settings -> General -> change visibility to **Public**.

## 8. Smoke test

- Visit https://niv.schendel.me -- site loads
- Visit https://chat.niv.schendel.me/ with a POST (or just check it responds)
- Open the site, click chat pill, send a message -- verify it works end to end
