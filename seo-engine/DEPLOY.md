# (Optional) Deploying a shared backend proxy

By default, `seo-engine.html` runs entirely from your own browser: click
"SET API KEY" in the page, paste your Anthropic API key, and it's stored
in that browser's `localStorage` only — never written to this repo. That's
the right setup for one person running it locally/privately on their own
device, and needs no deployment at all.

The downside of that default setup: the key lives in browser storage on
whatever device it's entered on, so don't enter it on a shared/public
computer or share that page's URL with the key already saved. If instead
you want multiple people to use the engine **without** any of them ever
seeing the API key, use this folder's `worker.js` — a small **Cloudflare
Worker** that holds the key server-side and streams the response back, and
point `seo-engine.html` at it instead of calling Anthropic directly.

This is a one-time setup (~10 minutes), done by whoever has (or creates) a
Cloudflare account and an Anthropic API key. I can't run these commands
myself — they need an interactive login and your own API key.

## Steps

1. **Get an Anthropic API key** (if you don't have one): https://console.anthropic.com/ → Settings → API Keys.

2. **Install Wrangler** (Cloudflare's CLI), if not already installed:
   ```
   npm install -g wrangler
   ```

3. **Log in to Cloudflare** (free account is fine):
   ```
   wrangler login
   ```

4. **Create the Worker project** using the existing `worker.js`:
   ```
   cd seo-engine
   wrangler init saps-seo-proxy --from-dot-env=false --yes
   # When prompted, choose "Hello World Worker" then replace the
   # generated src/index.js with the contents of worker.js in this folder.
   ```
   (Or simpler: `wrangler deploy worker.js --name saps-seo-proxy` from this folder.)

5. **Store the API key as a secret** (never goes into the repo):
   ```
   wrangler secret put ANTHROPIC_API_KEY
   ```
   Paste your Anthropic API key when prompted.

6. **Deploy**:
   ```
   wrangler deploy
   ```
   Wrangler prints a URL like `https://saps-seo-proxy.<your-account>.workers.dev`.

7. **Wire it up**: in `seo-engine.html`'s `runPhase()` function, change the
   `fetch("https://api.anthropic.com/v1/messages", ...)` call to
   `fetch("https://saps-seo-proxy.<your-account>.workers.dev", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ prompt: phase.prompt }) })`
   and drop the `x-api-key`/`anthropic-version` headers (the Worker adds
   those itself) — also remove the local "SET API KEY" requirement if you
   want this to be the only path.
   Also update `ALLOWED_ORIGIN` at the top of `worker.js` to match wherever
   `seo-engine.html` is actually hosted (e.g. `https://sapspoliceclearance.com`),
   then `wrangler deploy` again so the CORS check matches.

8. Commit and push the updated fetch call. The engine page will now call
   your Worker instead of Anthropic directly, and nobody needs their own
   API key to use it.

## Cost note
Each phase run is one Claude API call (~2000 output tokens max). Six phases
end-to-end is a small, predictable cost on your Anthropic account — there's
no recurring charge from Cloudflare Workers at this volume (well within the
free tier).
