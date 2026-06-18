/**
 * SAPS Police Clearance NZ — SEO Engine backend proxy.
 *
 * Holds the Anthropic API key server-side (as a Cloudflare Worker secret)
 * and forwards streaming requests from seo-engine.html, so the key is
 * never exposed to the browser. Deploy with the steps in DEPLOY.md.
 */

const ALLOWED_ORIGIN = "https://911duplessis.github.io"; // tighten to your actual Pages/site origin after first deploy
const MODEL = "claude-sonnet-4-20250514";
const MAX_TOKENS = 2000;

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") {
      return new Response(null, { headers: corsHeaders() });
    }

    if (request.method !== "POST") {
      return new Response("Method not allowed", { status: 405, headers: corsHeaders() });
    }

    let body;
    try {
      body = await request.json();
    } catch (e) {
      return new Response("Invalid JSON body", { status: 400, headers: corsHeaders() });
    }

    const prompt = body && body.prompt;
    if (!prompt || typeof prompt !== "string") {
      return new Response("Missing 'prompt' string in request body", { status: 400, headers: corsHeaders() });
    }

    const anthropicRes = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": env.ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01",
      },
      body: JSON.stringify({
        model: MODEL,
        max_tokens: MAX_TOKENS,
        stream: true,
        system: "You are a world-class SEO strategist and technical specialist. Produce structured, actionable, deployment-ready outputs. Use markdown headers, code blocks, and tables where they add clarity. Be specific — give real code, real URLs, real specifications. Never pad with generic advice.",
        messages: [{ role: "user", content: prompt }],
      }),
    });

    if (!anthropicRes.ok) {
      const errText = await anthropicRes.text();
      return new Response(errText, { status: anthropicRes.status, headers: corsHeaders() });
    }

    return new Response(anthropicRes.body, {
      status: 200,
      headers: {
        ...corsHeaders(),
        "Content-Type": "text/event-stream",
      },
    });
  },
};

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
  };
}
