# Deploying the SEO Engine backend proxy

`seo-engine.html` needs a live URL to send prompts to. It can't call the
Anthropic API directly — that would mean putting a secret API key in
browser JavaScript, where anyone can read it from the Network tab. Instead,
`worker.js` in this folder is a small **Cloudflare Worker** that holds the
API key on the server side and streams the response back.

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

7. **Wire it up**: open `seo-engine.html` at the repo root, find this line near
   the top of the `<script>` block:
   ```js
   const PROXY_URL = "";
   ```
   and set it to the Worker URL from step 6:
   ```js
   const PROXY_URL = "https://saps-seo-proxy.<your-account>.workers.dev";
   ```
   Also update `ALLOWED_ORIGIN` at the top of `worker.js` to match wherever
   `seo-engine.html` is actually hosted (e.g. `https://sapspoliceclearance.com`),
   then `wrangler deploy` again so the CORS check matches.

8. Commit and push the updated `PROXY_URL` line. The engine page will now
   show "Backend proxy configured." in its terminal log instead of the
   red warning banner, and phases will run for real.

## Cost note
Each phase run is one Claude API call (~2000 output tokens max). Six phases
end-to-end is a small, predictable cost on your Anthropic account — there's
no recurring charge from Cloudflare Workers at this volume (well within the
free tier).
