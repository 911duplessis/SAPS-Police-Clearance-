# (Optional) Backend proxy / API-key paths

By default, `seo-engine.html` runs in **manual mode**: no API key, no
backend, no cost. For each phase you click "Copy Prompt", paste it into
the free chat at [claude.ai](https://claude.ai/new), paste the reply back
into the page, and the phase is marked complete. Nothing ever leaves your
browser except the copy/paste you do by hand, and there's nothing to
deploy.

The options below are for anyone who'd rather automate the calls instead
of copy/pasting by hand — neither is required.

**Option 1 — your own API key, client-side only.** Wire `seo-engine.html`
to call `https://api.anthropic.com/v1/messages` directly from the browser
with a key entered via prompt and stored in that browser's `localStorage`
only (never written to this repo). Simple, but the key lives in browser
storage on whatever device it's entered on — don't use this on a
shared/public computer or share the page URL with the key already saved.

**Option 2 — shared backend proxy.** If multiple people need to run
phases **without** any of them ever seeing an API key, use this folder's
`worker.js` — a small **Cloudflare Worker** that holds the key server-side
and streams the response back, and point `seo-engine.html` at it instead
of calling Anthropic directly.

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
