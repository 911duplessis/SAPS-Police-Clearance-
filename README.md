# SAPS Police Clearance NZ

Marketing site for **South African Police Clearance (SAPS) & international fingerprint
coordination** from Christchurch, New Zealand. Fingerprint capture is performed by certified
partner technicians; the service coordinates the end-to-end clearance process.

**Live site:** https://sapspoliceclearance.com
**Hosting:** GitHub Pages (custom domain via `CNAME`), served directly from this repository.
**Stack:** Static, vanilla HTML/CSS/JS — no build step, no dependencies to install.

## Structure (flat layout)

| Path | Purpose |
|---|---|
| `index.html` | Main single-page site (hero, services, fingerprint, fast-track, about, FAQ, contact) |
| `christchurch.html` | SEO landing page — Christchurch |
| `how-long-does-it-take.html` | SEO landing page — timeline |
| `style.css` | Shared stylesheet for the public pages |
| `og-image.jpg` | 1200×630 social share / schema logo image |
| `robots.txt`, `sitemap.xml` | Crawl + indexing directives |
| `google2bbf502f984c3743.html` | Google Search Console verification |
| `seo-engine.html`, `seo-engine/` | Internal SEO helper tool + optional Cloudflare Worker proxy (noindex, robots-disallowed) |
| `progress-report.html` | Internal status page (noindex) |
| `CNAME` | Custom domain mapping |

## Local preview

```bash
git clone https://github.com/911duplessis/SAPS-Police-Clearance-.git
cd SAPS-Police-Clearance-
# open index.html in a browser, or:
python3 -m http.server 8000   # then visit http://localhost:8000
```

## Deploying

Pushes to the Pages-publishing branch go live automatically via GitHub Pages. There is no
build step — edit the HTML/CSS directly.

## Analytics & SEO

- Google Analytics 4 (`gtag.js`) and Search Console are configured on the public pages.
- On-page SEO: per-page `<title>`, meta description, canonical, Open Graph/Twitter tags, and
  JSON-LD structured data (Organization, LocalBusiness, FAQ, Breadcrumb).
- All contact CTAs are WhatsApp / `tel:` / `mailto:` deep links — the site has no forms and
  submits no user data to any endpoint.
