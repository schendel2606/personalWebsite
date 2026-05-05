# Production Setup

One-time steps to bring `niv.schendel.me` (canonical) and `chat.niv.schendel.me` live, with `schendel.me` and `www.schendel.me` permanently redirecting to the canonical site.

> **Important — order matters.** Complete steps 1, 2, and 6 (KV namespace + Worker secrets + GitHub Actions secret) **before** the first push to `main`. The CI workflows trigger on push and will fail noisily if any of those are missing or if `wrangler.toml` still contains the placeholder KV id. Suggested order: do all 7 setup steps locally on a feature branch, then merge to `main` to trigger the first deploy.

## 1. Cloudflare KV namespace

```bash
cd apps/chat-worker
npx wrangler login
npx wrangler kv:namespace create RATE_LIMIT_KV
```

Copy the returned `id` and replace `PLACEHOLDER_BIND_VIA_WRANGLER_KV_CREATE` in `apps/chat-worker/wrangler.toml`. Commit.

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

| Record to add / modify | Type | Name | Target | Proxy |
|---|---|---|---|---|
| **Add** (canonical site) | CNAME | `niv` | `schendel2606.github.io` | **DNS only** (gray) |
| **Modify** existing apex A records (×4) | A | `schendel.me` | (existing IPs) | **Proxied** (orange) |
| **Modify** existing `www` CNAME | CNAME | `www` | `schendel2606.github.io` | **Proxied** (orange) |

The apex + `www` toggle to Proxied is what lets the redirect Worker (route patterns in `wrangler.toml`) intercept those hostnames.

`chat.niv.schendel.me` is **not** added manually — it is created automatically by `wrangler deploy` as a Cloudflare-managed custom domain.

## 4. Cloudflare Worker routes

The `wrangler.toml` already declares three routes:

```toml
[[routes]]
pattern = "chat.niv.schendel.me"
custom_domain = true       # auto-creates DNS + cert

[[routes]]
pattern = "schendel.me/*"
zone_name = "schendel.me"  # uses existing proxied A records

[[routes]]
pattern = "www.schendel.me/*"
zone_name = "schendel.me"  # uses existing proxied www CNAME
```

The deploy is automated via GitHub Actions on push to `main`, but if you ever need to deploy locally:

```bash
cd apps/chat-worker && npx wrangler deploy
```

## 5. GitHub Pages config

In repo settings → Pages:
- Source: **GitHub Actions**
- Custom domain: `niv.schendel.me`
- Wait for the DNS check to pass (may take a few minutes)
- Enable **Enforce HTTPS** once available

## 6. GitHub Actions secret

In repo settings → Secrets and variables → Actions:
- Add: `CLOUDFLARE_API_TOKEN`
- Generate the token at <https://dash.cloudflare.com/profile/api-tokens>:
  - **Account → Workers Scripts → Edit**
  - **Account → Workers KV Storage → Edit**
  - **Account → Account Settings → Read**
  - **Zone → DNS → Edit**
  - **Zone → Workers Routes → Edit**
  - Account Resources: schendel.me's account
  - Zone Resources: `schendel.me` only

## 7. Repo visibility

Repo settings → General → change visibility to **Public**.

## 8. Smoke test

| URL | Expected |
|---|---|
| <https://niv.schendel.me> | Site loads (Hero + Projects + Experience + Resume + Contact) |
| <https://schendel.me> | 301 → `https://niv.schendel.me/` |
| <https://www.schendel.me> | 301 → `https://niv.schendel.me/` |
| <https://chat.niv.schendel.me/> with `POST` (or check OPTIONS preflight) | 4xx (rejects empty body) — proves the Worker is alive |
| Click the chat pill, send a message | Real reply from the agent |
| Send 11 messages quickly | 11th hits 429 with the polite fallback UI |

## 9. Optional: rotate secrets

If any secret was ever pasted into a chat / log / screenshot during setup, rotate it:

- **Anthropic key** — Anthropic console → API Keys → revoke + create new → `wrangler secret put ANTHROPIC_API_KEY` again
- **Cookie HMAC secret** — `openssl rand -hex 32` → `wrangler secret put SESSION_COOKIE_SECRET` again
- **Cloudflare API token** — dash.cloudflare.com/profile/api-tokens → roll → update GitHub Actions secret
