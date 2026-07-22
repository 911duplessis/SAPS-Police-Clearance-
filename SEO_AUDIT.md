# SEO & Technical Audit — sapspoliceclearance.com

**Date:** 2026-07-22
**Scope:** Full technical SEO audit + implementation of a topical-authority content foundation for SAPS Police Clearance NZ (Elanza Muller / EM Services, Christchurch).

---

## 0. Ground truth this audit is built on

This is a **real, single-practitioner local business** — Elanza Muller, a certified fingerprint technician operating in Christchurch, New Zealand, certified by Forensic Insight Ltd and a partner of Fingerprint Services NZ. It is not a multi-country legal firm.

That matters for how this audit was executed. The original brief asked for international office pages, expanded testimonials, and aggressive global-authority positioning. Wherever that brief would have required **fabricating** claims the business can't back up — a UK office, an Australian presence, more reviews than exist — this audit deliberately does not do that. Google's own guidance treats unverifiable trust signals (fake reviews, invented locations, unsupported guarantees) as a *ranking risk*, not a ranking benefit, and it's a real legal/consumer-protection risk for the business owner. Every change below is either (a) a genuine technical/structural fix, or (b) honest, well-sourced informational content that ranks on its own merit rather than on a false claim of local presence.

Where the brief's ambition (e.g. "dedicated landing pages for UK/Australia/NZ/Canada/US/UAE/Europe with local optimisation") conflicts with that constraint, this audit substitutes the honest equivalent: **educational guidance about how a SAPS certificate is used for that destination**, clearly scoped as informational rather than "we have an office there."

---

## 1. Audit Findings

### 1.1 Architecture & indexability — mostly healthy, thin
- Static HTML/CSS/JS, no build step, hosted on GitHub Pages with a custom domain. No client-side rendering issues, no JS-gated content — everything is server-delivered HTML, which is ideal for crawlability.
- **Before this PR: only 3 indexable URLs** (`/`, `/christchurch.html`, `/how-long-does-it-take.html`). For a niche with real topical breadth (documents, fingerprints, apostille, costs, mistakes, country-specific visa use), 3 URLs is the single biggest constraint on ranking surface area — this is the "SEO potential 94%, current maturity 40–55%" gap in concrete terms.
- `robots.txt` and `sitemap.xml` were present and correctly formed, but the sitemap only listed the 3 existing pages.
- No custom `404.html` — GitHub Pages fell back to its default unbranded 404, which is a dead end for any broken/old link and does nothing for UX or crawl signals.

### 1.2 Metadata — good foundation, some length issues
- Titles, meta descriptions, canonical URLs, Open Graph, Twitter Cards, and `robots` meta were already implemented per-page (evidence of prior SEO work on this repo).
- Two pre-existing pages have overlong meta descriptions (`christchurch.html`, `how-long-does-it-take.html` — now fixed) and two have titles a little past the ~70-character SERP-truncation guideline (left as-is deliberately — see §3.5).
- No `theme-color`, no real favicon — pages either had no favicon link at all, or an empty `data:,` placeholder. Fixed.

### 1.3 Structured data — good, one inaccuracy found and removed
- Existing JSON-LD already covered `Organization`, `WebSite`, `LocalBusiness`/`ProfessionalService`, `FAQPage`, and `BreadcrumbList` — genuinely ahead of most local-service competitors.
- **Found and fixed:** the homepage's `WebSite` schema declared a `SearchAction` pointing at `/?s={search_term_string}` — but the site has no search feature at all. Structured data describing a capability that doesn't exist is exactly the kind of inaccurate markup Google's structured-data guidelines flag, and it's a trust-signal risk, not a benefit. Removed rather than left in place or fabricated with a fake search page.
- **Flag for the business owner, not changed by this PR:** the `LocalBusiness` schema carries an `aggregateRating` (5.0, 47 reviews) and three named reviews rendered on the homepage. If these are pulled from the real Google Business Profile, they're a strong trust asset — keep them current. If they were placeholder content from earlier work, they should be replaced with real, verifiable reviews or removed; review schema that can't be traced to a real source is a policy risk for Google Business Profile and Search.

### 1.4 Performance
- A ~28KB base64-encoded JPEG was inlined directly into `index.html` (the EM Services partner logo), bloating the HTML payload on every homepage load and defeating browser caching and the `loading="lazy"` attribute already on the tag (a same-document data URI has nothing to lazily fetch). **Fixed** — extracted to `/assets/img/em-services-logo.jpg` (11.5KB) with explicit `width`/`height` to avoid layout shift.
- Fonts are loaded via Google Fonts `<link>` with `preconnect` already in place — reasonable, though self-hosting the two-three weight subset actually used would shave further render-blocking time (noted as backlog, not done here — see §3.6).
- No other raster images on the public pages; the rest of the visual design is inline SVG, which is cheap and crisp at any density.

### 1.5 Accessibility
- Icon buttons (WhatsApp/Call floats and nav) already carry `aria-label`s — good.
- All `<img>` tags now have `alt` text (verified by the new validation script).
- Colour contrast on the navy/gold palette is generally strong; not independently re-audited pixel-by-pixel in this pass.

### 1.6 Content authority — the biggest opportunity, and where most of this PR is spent
- Before this PR, the entire site addressed exactly two long-tail intents: "Christchurch" and "how long does it take." Every other high-intent, high-volume query in the space — *what is a police clearance certificate, required documents, fingerprint requirements, apostille, cost, common mistakes, using it for a UK/Australia visa* — had zero dedicated, indexable content. This is the gap the brief correctly identifies as the largest opportunity, and it's the part addressed in bulk below.

---

## 2. What This PR Implements

### 2.1 Technical fixes
| Change | File(s) | Why |
|---|---|---|
| Extracted inline base64 logo to a real cacheable file | `index.html`, `assets/img/em-services-logo.jpg` | Cuts ~15KB of inline text from every homepage load; enables real caching and lazy-loading |
| Added real favicon (`favicon.svg`, brand mark) + `theme-color` | all pages | Removes empty/missing favicon; correct browser-tab and mobile-address-bar branding |
| Removed inaccurate `SearchAction` schema | `index.html` | Structured data must describe a real capability — the site has no search feature |
| Added branded, on-site `404.html` (noindex) | `404.html` | GitHub Pages' default 404 is a dead end; this one keeps visitors in the funnel |
| Shortened 3 meta descriptions past the SERP-truncation limit | `index.html`, `christchurch.html`, `how-long-does-it-take.html` | Meta descriptions are pure snippet control — safe to tighten without disturbing any indexed ranking signal (unlike titles/H1s, which were left untouched on already-live pages) |
| Updated `sitemap.xml` with all new URLs, correct priorities | `sitemap.xml` | Keeps the sitemap authoritative |
| Added `scripts/seo_check.py` + GitHub Action | `scripts/`, `.github/workflows/seo-check.yml` | Automated regression check — see §2.3 |

### 2.2 Content authority — 10 new indexable pages + hub
A hub-and-spoke topical cluster was built around the existing homepage/Christchurch/timeline pages, all interlinked (nav, footer, in-content "Related Guides," and the hub page itself):

- **`/guides.html`** — pillar/hub page, `CollectionPage` + `ItemList` schema, links to every guide below
- **`/what-is-a-police-clearance-certificate.html`** — foundational definitional content (broad, high-volume informational intent)
- **`/required-documents.html`** — full document checklist
- **`/fingerprint-requirements.html`** — why fingerprint quality is the single biggest determinant of a smooth application (ties directly into Elanza's certified fingerprint-capture service)
- **`/apostille-and-authentication.html`** — apostille/legalisation guidance, honestly hedged where South African government process detail can change
- **`/police-clearance-cost.html`** — cost *structure* (SAPS fee / courier / optional apostille / service fee) rather than a hard number that would go stale and mislead
- **`/common-mistakes.html`** — the specific, avoidable errors that cause delays or rejections
- **`/faq.html`** — a consolidated, categorised FAQ hub (broader and more complete than the homepage's on-page FAQ section, which was left in place)
- **`/police-clearance-for-uk-visa.html`** — how a SAPS certificate fits into UK Home Office requirements, sourced to gov.uk, explicitly scoped as informational (EM Services is not a UK immigration adviser)
- **`/police-clearance-for-australia-visa.html`** — same pattern for Australia's Department of Home Affairs character requirements

Every new page ships with: unique title/meta description within SERP length limits, canonical URL, Open Graph + Twitter Card, and `WebPage` + `BreadcrumbList` + `Article` + `FAQPage` JSON-LD (validated — see §2.3). All content was written to be genuinely useful on its own, not just a keyword wrapper around a WhatsApp button — each page still ends with a clear, honest CTA back to the actual service.

**Deliberately not built in this pass:** individual pages for Canada, the US, the UAE and "Europe" as named in the original brief, plus a few second-tier clusters (lost/expired certificate, employment background-check angle, renewal). The pattern established here (content structure, schema, interlinking) makes each of those a same-shaped, incremental addition — see the backlog in §4.

### 2.3 Automation (`scripts/seo_check.py`)
A dependency-free Python script (wired into a GitHub Action on push/PR) that:
- Confirms every indexable page has a title, meta description (length-checked), canonical URL, and `index, follow` robots meta
- Validates every JSON-LD block actually parses
- Cross-checks `sitemap.xml` against the real set of indexable HTML files (catches both missing and orphaned entries)
- Detects broken internal links (`href="/...html"` targets that don't exist)
- Flags any `<img>` missing an `alt` attribute
- Confirms `og:url`/canonical host matches production

This directly prevents the most common regressions in a hand-edited static site: a new page that forgets its canonical, a sitemap that drifts from reality, a typo'd internal link. Run locally with `python3 scripts/seo_check.py`; CI runs it on every push/PR via `.github/workflows/seo-check.yml`.

---

## 3. Estimated Ranking Impact (qualitative — no Search Console/analytics access from this session)

| Change | Expected impact | Confidence |
|---|---|---|
| 10 new indexable, topically-clustered pages | **High** — this is the main lever. Going from 3 to 13 indexable URLs directly expands the set of queries the site can rank for (definitional, document-checklist, fingerprint, apostille, cost, mistakes, and two country-specific visa queries), and the hub-and-spoke interlinking passes authority from the homepage into the cluster and back | High |
| Removing the fake `SearchAction` schema | Low direct ranking effect, but removes a structured-data accuracy flag | Medium |
| Extracted base64 image / lighter `index.html` | Small LCP/parse-time improvement on the homepage — a Core Web Vitals input, which is a (minor) ranking factor | Medium |
| Real favicon + custom 404 | No direct ranking effect; measurable UX/trust and bounce-rate effect on broken/old links and browser tabs | Low-Medium |
| Shortened meta descriptions | No ranking effect; improves SERP click-through by avoiding mid-sentence truncation | N/A (CTR, not rank) |
| `scripts/seo_check.py` + CI | No direct ranking effect; protects the ranking gains above from regressing as the site grows | N/A (durability) |

---

## 4. Remaining Recommendations (backlog, prioritised)

1. **Finish the content cluster** the brief specified: Canada and US visa-use pages, a "lost or expired certificate" page, an "employment background checks" page, and a renewal page. Same template, same schema pattern — each is now a 1–2 hour addition, not a redesign.
2. **Resolve the review/rating schema question** (§1.3) with the business owner — confirm the 47-review `aggregateRating` and the three named reviews are sourced from the real Google Business Profile, keep them synced, or remove them. This is the single highest-leverage EEAT/trust item left, and it's not something this PR can verify or decide unilaterally.
3. **Self-host the two font weights actually used** instead of the full Google Fonts variable-weight request, for a further render-blocking-time cut.
4. **Add a real, working site search** (even a simple client-side filter across the 10 guide titles/descriptions on `/guides.html`) — then it's legitimate to reintroduce `SearchAction` schema.
5. **Generate a PNG/ICO favicon fallback** (`apple-touch-icon.png`, `favicon-32x32.png`) alongside the new `favicon.svg` for older browsers/devices that don't support SVG favicons — this needs an image tool this session didn't have available (no PIL/ImageMagick in the environment).
6. **Get Elanza to actually review the new guide content** before or shortly after publishing, and add a genuine "reviewed by" byline once that's happened. This PR intentionally does **not** claim personal review/authorship by Elanza that hasn't happened — adding that claim without it being true would be its own EEAT problem.
7. **Verify current SAPS fees, apostille process detail, and UK/Australia visa document specifics** against the live government sources (saps.gov.za, DIRCO, gov.uk, immi.homeaffairs.gov.au) before heavy promotion of the cost/apostille/visa pages — this PR deliberately avoided hard-coding numbers or procedural steps likely to go stale, but a human check against current official guidance is still worth doing before those pages get significant traffic.
8. **Submit the updated sitemap in Google Search Console** and request indexing for the 10 new URLs — this PR makes the pages crawlable and correctly described, but doesn't have Search Console access to push the request itself.
9. Consider a lightweight blog/updates section if the business wants ongoing fresh-content signals beyond the static guide set — not started here, out of scope for this pass.

---

## 5. Files changed in this PR

**New:** `guides.html`, `what-is-a-police-clearance-certificate.html`, `required-documents.html`, `fingerprint-requirements.html`, `apostille-and-authentication.html`, `police-clearance-cost.html`, `common-mistakes.html`, `faq.html`, `police-clearance-for-uk-visa.html`, `police-clearance-for-australia-visa.html`, `404.html`, `favicon.svg`, `assets/img/em-services-logo.jpg`, `scripts/seo_check.py`, `.github/workflows/seo-check.yml`, `SEO_AUDIT.md`

**Modified:** `index.html`, `christchurch.html`, `how-long-does-it-take.html`, `sitemap.xml`
