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
| `guides.html` | Guides hub — pillar page linking the full content cluster below |
| `what-is-a-police-clearance-certificate.html` | Guide — what the certificate is and who needs one |
| `required-documents.html` | Guide — full document checklist |
| `fingerprint-requirements.html` | Guide — fingerprint capture standard and why it matters |
| `apostille-and-authentication.html` | Guide — apostille/legalisation for overseas use |
| `police-clearance-cost.html` | Guide — cost structure breakdown |
| `common-mistakes.html` | Guide — common application mistakes and how to avoid them |
| `faq.html` | Consolidated, categorised FAQ hub |
| `police-clearance-for-uk-visa.html` | Guide — using a SAPS certificate for a UK visa |
| `police-clearance-for-australia-visa.html` | Guide — using a SAPS certificate for an Australian visa |
| `404.html` | Branded not-found page (noindex) |
| `style.css` | Shared stylesheet for the public pages |
| `favicon.svg` | Site favicon (brand mark) |
| `og-image.jpg` | 1200×630 social share / schema logo image |
| `assets/img/` | Site images (e.g. partner logo) |
| `robots.txt`, `sitemap.xml` | Crawl + indexing directives |
| `google2bbf502f984c3743.html` | Google Search Console verification |
| `seo-engine.html`, `seo-engine/` | Internal SEO helper tool + optional Cloudflare Worker proxy (noindex, robots-disallowed) |
| `progress-report.html` | Internal status page (noindex) |
| `scripts/seo_check.py` | Dependency-free SEO/technical-hygiene validator — run locally or via CI (see below) |
| `SEO_AUDIT.md` | Full SEO audit, priority roadmap and change log |
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
  JSON-LD structured data (Organization, WebSite, LocalBusiness/ProfessionalService, Article,
  FAQ, Breadcrumb, CollectionPage on the guides hub).
- All contact CTAs are WhatsApp / `tel:` / `mailto:` deep links — the site has no forms and
  submits no user data to any endpoint.
- Run `python3 scripts/seo_check.py` before publishing new pages — it checks title/meta/canonical/
  robots presence, validates every JSON-LD block, cross-checks `sitemap.xml` against the real set
  of indexable pages, and flags broken internal links or missing image `alt` text. It also runs
  automatically on push/PR via `.github/workflows/seo-check.yml`.
- See `SEO_AUDIT.md` for the full audit, what changed, and the prioritised backlog.
