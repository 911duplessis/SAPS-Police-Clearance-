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

---
---

# Phase 2 — Domain/Search Console Audit, EEAT, Accessibility & Automation

**Date:** 2026-07-23
**Scope:** Repository consolidation is complete — `911duplessis/SAPS-Police-Clearance-` is the sole, permanent repository. This phase covers a Search Console / domain-integrity audit, EEAT infrastructure (Privacy/Terms), structured-data expansion, visible internal linking (breadcrumbs, HTML sitemap), accessibility fixes, a real font-loading bug, and stronger CI validation.

## 1. Domain integrity audit (in response to the misspelled-domain question)

**The repository itself is clean.** A full-text search across every canonical URL, Open Graph tag, JSON-LD block, `sitemap.xml`, `robots.txt`, and internal `href` in this repo turns up **zero** occurrences of the misspelled `sapspoliceclearence.com` in any functional SEO surface. Every canonical/OG URL in the codebase resolves to `https://sapspoliceclearance.com`. A permanent regression guard for this was added to `scripts/seo_check.py` (`MISSPELLED_DOMAIN` check) so it can never silently reappear.

**The typo domain is a real, separate, still-live problem — but it isn't in this repo.** An internal status page already in the repo (`progress-report.html`, noindex, written by an earlier session) documents that two duplicate deployments still exist under the `iamstiaan` GitHub account and were never addressed:
- `iamstiaan/Sapspoliceclearancenz` — CNAME'd directly to the misspelled `sapspoliceclearence.com`, still live
- `iamstiaan/SAPS-Clear` — a third, undiscussed duplicate

This is exactly the same category of problem as `iamstiaan/SAPS-Police-Clearance-legacy`, which you already deleted earlier in this session. That's almost certainly why Search Console shows a second `sc-domain:sapspoliceclearence.com` property — it's a genuinely separate, still-serving website, not a misconfiguration in this repo. **Recommended fix, same playbook as before:** log into `iamstiaan`, confirm neither repo is needed, and delete them (or transfer + rename if you want to preserve them as inert archives). I can't do this myself — no credentials for that account, and repo-transfer/deletion has to happen in your browser.

## 2. The 3 Search Console "page with redirect" URLs

I don't have Search Console access in this session, so I can't see the exact 3 URLs — but I can rule in/out likely causes from what's actually deployed:

- No `_redirects` file, no `<meta http-equiv="refresh">`, and no server-side redirect config exists anywhere in this repo — this is a static GitHub Pages site with none of the usual self-inflicted redirect problems.
- GitHub Pages **automatically** issues redirects for: (a) `http://` → `https://` once HTTPS is enforced, (b) the `www.sapspoliceclearance.com` variant → the apex domain, and (c) the fallback `911duplessis.github.io/SAPS-Police-Clearance-/...` address → the custom domain. That's three plausible, entirely expected redirect sources — and notably, an earlier internal note (inside `seo-engine.html`, an internal tool page) explicitly discusses confirming `www.sapspoliceclearance.com` as a redirect target, confirming the `www` variant is a live, intentional redirect.
- **My assessment: these 3 are very likely benign, expected redirects, not errors** — Search Console's "Page with redirect" status is informational (it means Google found a URL and correctly followed a redirect), not necessarily something to fix, *unless* one of those 3 URLs is what's actually listed in `sitemap.xml` (a sitemap should only ever list final, 200-status canonical URLs). I've verified `sitemap.xml` only lists the canonical `https://sapspoliceclearance.com/...` form, so that's not the case here.

**To close this out with certainty**, paste me the 3 exact URLs from Search Console's Page Indexing → "Page with redirect" report and I'll give you a definitive verdict on each rather than a general one.

## 3. Google Business Profile consistency (real bug found and fixed)

You confirmed the real GBP is **"SAPS Police Clearance NZ"**, Canterbury Region, NZ. Checking the code against that:

- The homepage's visible Google Business Profile section already correctly links `g.page/r/sapspoliceclearancenz` (matching reviews + "leave a review" links) — this was already right.
- **Bug found:** the `Organization` schema's `sameAs` — which is *also* named "SAPS Police Clearance NZ" — was pointing at `g.page/em-services-nz` instead, a differently-named profile (EM Services is credited elsewhere on the page as the separate holding-company entity, which is a legitimate distinct profile, just not the one this particular schema node represents). **Fixed:** both `Organization` and `LocalBusiness` schema now correctly `sameAs` the actual "SAPS Police Clearance NZ" profile (`g.page/r/sapspoliceclearancenz`), matching the entity name in both places. The EM Services partner-card link elsewhere on the page was left untouched, since it's correctly labelled as EM Services' own profile.
- This is exactly the NAP (Name/Address/Phone)-consistency signal you asked about — business name, address (Christchurch, Canterbury, NZ), and now the Business Profile link all agree between the live site, its structured data, and the real GBP.
- On the existing `aggregateRating` (5.0, 47 reviews): the same internal progress report confirms this was sourced from real competitor/business research in an earlier session, not fabricated during content generation — which is reassuring context, but I still can't independently re-verify it's live-synced to the current GBP rating from this session. Worth a human glance at the actual profile to confirm the number hasn't drifted; not changed here.

## 4. What else shipped in Phase 2

| Change | Why |
|---|---|
| **Privacy Policy + Terms of Service pages** (`/privacy-policy.html`, `/terms-of-service.html`) | The biggest EEAT gap from Phase 1 — accurate, honest description of GA4 use, no invented data-handling claims, service disclaimers, NZ governing law |
| **HTML sitemap page** (`/sitemap.html`) | Human-readable index of every page; another internal-linking pass |
| **Visible breadcrumb trail** on every subpage (`<nav aria-label="Breadcrumb">`), matching the existing JSON-LD | Was schema-only before; now a real, crawlable, accessible UI element with anchor-text internal links |
| **`Person` schema for Elanza**, linked as `employee` on both `Organization` and `LocalBusiness` | Attributes expertise to a real, named, credentialed individual — genuine E-E-A-T, not fabricated |
| **Explicit `ImageObject` schema** for the logo/OG image, referenced by `@id` from `Organization`/`LocalBusiness`/`Person` | Requested in the original brief, never implemented until now |
| **`HowTo` schema** for the homepage's 5-step process | Legitimate rich-result candidate (noting Google reduced how often `HowTo` renders as a visible SERP feature in 2023 — still valid, correct markup either way) |
| **`lost-or-expired-certificate.html`** — one new guide | Distinct, common search intent nothing else on the site covered; not padding — everything else in the Phase 1 backlog (Canada/US/UAE pages) was deliberately held back |
| **Fixed a real font-rendering bug**: `Outfit` weight 800 is used on the logo and every primary CTA button but was never requested from Google Fonts (browsers were faux-bolding it); `Space Mono` italic was requested but used nowhere. Both fixed across all 20 pages | Visible-UI rendering quality + a small payload trim |
| **Skip-to-content link** + `id="main"` on every `<main>` (added a real `<main>` landmark to the homepage, which didn't have one) | Baseline keyboard/screen-reader accessibility that was missing |
| **`scripts/seo_check.py` expanded**: single-`<h1>` check, `<html lang>` check, `target="_blank"` without `rel="noopener"` check, duplicate title/meta-description detection across pages, and the misspelled-domain regression guard | Catches the failure modes most likely to creep in as the page count grows |
| **Footer legal links** (Privacy · Terms · Sitemap) added to every page | Standard, expected trust-signal placement |

Full validation: `scripts/seo_check.py` → 0 errors across all 20 pages (2 pre-existing, deliberately-untouched title-length warnings on already-indexed pages carried over from Phase 1).

## 5. Prioritised roadmap — what's left

| Recommendation | Impact | Effort |
|---|---|---|
| Delete/retire `iamstiaan/Sapspoliceclearancenz` and `iamstiaan/SAPS-Clear` | **High** — removes a genuine duplicate-content/typo-domain liability in Search Console | Low (same delete flow already used once) |
| Confirm the 3 GSC redirect URLs and close out validation | **High** — directly unblocks the one flagged Search Console issue | Low (needs the 3 URLs from you) |
| Verify the 47-review `aggregateRating` still matches the live GBP rating | **Medium** — EEAT/trust accuracy | Low (a human glance at the GBP) |
| Finish the content cluster: Canada/US/UAE visa-use pages, employment background-check page | **Medium** — broadens topical coverage, same proven template | Medium |
| Self-host the actual font subset instead of the Google Fonts CDN request | **Medium** — further Core Web Vitals/LCP improvement | Medium-High (needs font subsetting tooling not available in this environment) |
| Add a working client-side search on `/guides.html`, then reinstate `SearchAction` schema | **Low-Medium** — legitimate rich-result + UX improvement | Medium |
| Secure `sapspoliceclearance.co.nz` (already recommended in the earlier competitor audit) | **Low-Medium** — defensive/brand, not urgent | Low (registration only, no dev work) |
| PNG/ICO favicon fallback alongside the new `favicon.svg` | **Low** — cosmetic, older-browser only | Low (needs image tooling not available in this environment) |
| Get Elanza to actually review new guide content, then add a genuine "reviewed by" byline | **Low direct SEO impact, meaningful EEAT** | Low effort, but needs her time, not mine |

---
---

# Phase 3 — Indexing Focus: Glossary, Internal Linking Depth, Robots/Orphan Automation

**Date:** 2026-07-23
**Scope:** Per direction — deprioritise `iamstiaan` repo cleanup unless it's actively causing confusion (noted, not acted on this phase), and focus on Google's understanding of the already-built site: crawlability, internal linking depth, and stronger CI. Item 1 (per-URL redirect investigation) is **pending** — the 3 Search Console URLs haven't been provided yet; this phase covers items 2–5.

## 1. CI status check

Confirmed via the Actions API rather than assumed: the `seo-check` workflow ran and passed on both the Phase 2 pull request and the resulting push to `Index` (run IDs `29967666530` and `29967924559`, both `completed`/`success`). The validation pipeline is genuinely running, not just configured.

**One gap I can't close myself**: there's no tool available in this session for repo-admin actions like branch protection, so I can't confirm or set up "require the seo-check status check to pass before merge." If that isn't already configured, it's a two-minute setting: repo **Settings → Branches → Branch protection rule → `Index` → Require status checks to pass → select `seo-check`**. Worth doing once, since it's exactly what turns "CI runs" into "CI actually gates merges."

## 2. Fresh audit findings

Going back through every category from the brief against the current merged state:

- **Technical SEO / Crawlability / Indexation**: solid. Robots.txt, sitemap, canonicals all consistent (now with automated checks — see §4). No pagination, no hreflang needed (single language/region). No orphaned pages (verified, not assumed — see §4).
- **EEAT**: Privacy/Terms/GBP consistency covered in Phase 2. The one item still outstanding is the same one flagged twice already — confirming the `aggregateRating`/review content against the live GBP — not something I can resolve from here.
- **Structured Data / Rich Results**: `DefinedTermSet`/`DefinedTerm` added for the new glossary (the correct schema.org type for a glossary page, and a genuine rich-result candidate). Everything else from the original checklist (Organization, WebSite, LocalBusiness, Article, FAQPage, BreadcrumbList, HowTo, Person, ImageObject, CollectionPage, ItemList) was already in place after Phase 2.
- **Core Web Vitals**: nothing new to fix without tooling this environment doesn't have (font subsetting) — already flagged in the Phase 2 backlog, unchanged.
- **Internal Linking**: this was the real gap. The homepage's service cards (SAPS Police Clearance, Fingerprint Capture, Fast Track, Document Preparation, Multi-Purpose Clearance) had zero links into the deep guide content — a visitor reading the homepage had no path into the guides cluster except the nav bar. Fixed (see §3).
- **Accessibility**: covered in Phase 2 (skip link, `<main>` landmarks, breadcrumb nav). No further gaps found that don't require a real browser-based tool (contrast-ratio auditing) this environment doesn't have.
- **Conversion Optimisation**: CTA density and consistency were already strong; didn't force additional changes here — more CTAs isn't the lever right now, more findable content is.

## 3. What shipped this phase

| Change | Why |
|---|---|
| **`glossary.html`** — ~20-term glossary (PCC, SAPS, Criminal Record Centre, Apostille, DIRCO, biometric/ID terms, and UK/Australia/Canada immigration-authority terms), with `DefinedTermSet` schema | Ties the entire site together — nearly every term links to the guide that explains it in depth. Genuine "what does X mean" long-tail search intent nothing else on the site captured, and glossaries are a hallmark of sites Google treats as topically authoritative |
| **`police-clearance-for-canada-immigration.html`** | Completes the UK/Australia/Canada trio using the same honest, informational-not-local-presence template — IRCC's police certificate requirement is real, common, and distinct from the UK/AU cases |
| **Homepage service cards now link to their matching deep guide** (SAPS Police Clearance → what-is-a-PCC, Fingerprint Capture → fingerprint-requirements, Fast Track → how-long-does-it-take, Document Preparation → required-documents, Multi-Purpose Clearance → guides hub) | Closes the internal-linking gap found in §2 — this is the single highest-leverage crawl/authority-flow fix this phase, since the homepage is where all external authority lands first |
| **Cross-links added**: UK ↔ Australia ↔ Canada guides now reference each other; what-is-a-PCC now links to the glossary | Denser topical mesh — each new page reinforces 2–3 existing ones and vice versa |
| **`scripts/seo_check.py`: robots.txt validation** | Confirms `robots.txt` references the real `sitemap.xml` and doesn't accidentally `Disallow` any indexable page — a config typo here would be invisible without this |
| **`scripts/seo_check.py`: orphan-page detection** | Builds the actual internal link graph from `index.html` and flags any indexable page a crawler can't reach by following links alone (not just via the sitemap) — directly caught the homepage-to-guides gap described in §2 before it was fixed, and will catch any future page that gets built but never linked |

Full validation: `scripts/seo_check.py` → 0 errors across all 22 pages (same 2 pre-existing title-length warnings, unchanged, still deliberately left alone).

## 4. Still pending — needs your input

**Item 1, Search Console redirect investigation**: ready to go the moment you paste the 3 flagged URLs. Per-URL, I'll check: why Google reports it as a redirect, whether it should be a direct 200 instead, canonical tag, sitemap presence, internal links pointing at it, and whether the final destination is indexable — exactly as specified, root cause before any fix.

## 5. Updated priority backlog

| Recommendation | Impact | Effort |
|---|---|---|
| Confirm the 3 GSC redirect URLs | **High** — the one open Search Console item | Low (needs the 3 URLs) |
| Enable "require seo-check to pass" branch protection on `Index` | **Medium-High** — turns passive CI into an actual merge gate, directly what was asked for | Low (repo Settings, 2 minutes) |
| Verify the 47-review `aggregateRating` against the live GBP | **Medium** — EEAT accuracy | Low (a human glance) |
| Add employment background-check guide, lost-certificate-style depth for remaining edge cases | **Low-Medium** | Medium |
| Self-host fonts | **Medium** (CWV) | Medium-High (needs tooling not in this environment) |
| `iamstiaan` duplicate cleanup | **Low priority per current direction** — revisit only if it starts causing workflow confusion | Low, whenever it's convenient |
