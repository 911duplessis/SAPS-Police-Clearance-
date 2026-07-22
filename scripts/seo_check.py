#!/usr/bin/env python3
"""
Build-time SEO / technical-hygiene validator for sapspoliceclearance.com.

Pure stdlib, no dependencies, no build step required — this only *checks*
the static HTML that's already committed. Run it locally or in CI:

    python3 scripts/seo_check.py

Exits non-zero if any error-level issue is found (warnings do not fail
the build). Checks performed:

  1. Every indexable HTML page has: <title>, meta description, canonical
     link, meta robots, and valid title/description lengths.
  2. Every <script type="application/ld+json"> block parses as valid JSON.
  3. sitemap.xml lists every indexable page and nothing extra/missing.
  4. Internal links (href="/...") resolve to a real file in the repo.
  5. <img> tags have an alt attribute.
  6. og:url / canonical host matches the production domain.
  7. Exactly one <h1> per indexable page.
  8. <html> has a lang attribute.
  9. target="_blank" links carry rel="noopener" (tabnapping / SEO hygiene).
  10. No two indexable pages share an identical <title> or meta description
      (duplicate metadata dilutes ranking signals and confuses SERP snippets).
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOMAIN = "https://sapspoliceclearance.com"
MISSPELLED_DOMAIN = "sapspoliceclearence"  # "clearence" — a real typo domain exists; never reference it

# Pages that intentionally opt out of indexing / full checks.
NOINDEX_ALLOWED = {"404.html", "progress-report.html", "seo-engine.html"}
SKIP_ENTIRELY = {"google2bbf502f984c3743.html"}  # verification file, not a real page

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def warn(msg):
    warnings.append(msg)


def html_files():
    for name in sorted(os.listdir(ROOT)):
        if name.endswith(".html") and name not in SKIP_ENTIRELY:
            yield name


def get_meta(html, name=None, prop=None):
    attr, value = ("name", name) if name else ("property", prop)
    # Backreference on the quote char so values containing an apostrophe
    # (e.g. "Australia's") don't prematurely terminate the match.
    m = re.search(rf'<meta\s+{attr}=(["\']){re.escape(value)}\1\s+content=(["\'])(.*?)\2', html, re.I)
    return m.group(3) if m else None


def expected_canonical(name):
    return f"{DOMAIN}/" if name == "index.html" else f"{DOMAIN}/{name}"


def check_page(name):
    path = os.path.join(ROOT, name)
    html = open(path, encoding="utf-8").read()

    # Misspelled domain must never appear anywhere on the live site — a
    # real typo-domain duplicate exists off-repo; don't accidentally link it.
    if MISSPELLED_DOMAIN in html.lower() and name != "progress-report.html":
        err(f"{name}: references the misspelled domain ({MISSPELLED_DOMAIN}...) — should be sapspoliceclearance")

    if "<html" in html and not re.search(r"<html[^>]*\slang=", html, re.I):
        err(f"{name}: <html> tag missing lang attribute")

    h1_count = len(re.findall(r"<h1\b", html))
    if name not in NOINDEX_ALLOWED and h1_count != 1:
        err(f"{name}: expected exactly 1 <h1>, found {h1_count}")

    for a_tag in re.findall(r'<a\b[^>]*>', html):
        if 'target="_blank"' in a_tag and "rel=" in a_tag and "noopener" not in a_tag:
            err(f"{name}: target=\"_blank\" link missing rel=\"noopener\" — {a_tag[:90]}")
        elif 'target="_blank"' in a_tag and "rel=" not in a_tag:
            err(f"{name}: target=\"_blank\" link missing rel=\"noopener\" — {a_tag[:90]}")

    title_m = re.search(r"<title>(.*?)</title>", html, re.S)
    if not title_m:
        err(f"{name}: missing <title>")
    else:
        title = title_m.group(1).strip()
        if not (10 <= len(title) <= 70):
            warn(f"{name}: title length {len(title)} chars (recommended 10-70) — {title!r}")

    robots = get_meta(html, name="robots")
    canonical_m = re.search(r'<link\s+rel=["\']canonical["\']\s+href=(["\'])(.*?)\1', html, re.I)
    canonical = canonical_m.group(2) if canonical_m else None

    if name in NOINDEX_ALLOWED:
        if not robots or "noindex" not in robots:
            warn(f"{name}: expected noindex robots meta on an internal/error page")
    else:
        desc = get_meta(html, name="description")
        if not desc:
            err(f"{name}: missing meta description")
        elif not (50 <= len(desc) <= 165):
            warn(f"{name}: meta description length {len(desc)} chars (recommended 50-165)")

        if not robots or "noindex" in robots:
            err(f"{name}: indexable page missing 'index, follow' robots meta (found {robots!r})")
        if not canonical:
            err(f"{name}: missing canonical link")
        elif canonical != expected_canonical(name):
            err(f"{name}: canonical {canonical!r} does not match expected {expected_canonical(name)!r}")

        og_url = get_meta(html, prop="og:url")
        if og_url and not og_url.startswith(DOMAIN):
            err(f"{name}: og:url host mismatch — {og_url}")

    # JSON-LD validity
    for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
        try:
            json.loads(block)
        except json.JSONDecodeError as e:
            err(f"{name}: invalid JSON-LD — {e}")

    # img alt attributes
    for img in re.findall(r"<img\b[^>]*>", html):
        if "alt=" not in img:
            err(f"{name}: <img> missing alt attribute — {img[:80]}")

    # internal links resolve to a real file
    for href in re.findall(r'href=["\'](/[a-zA-Z0-9_\-./]+\.html)(?:#[^"\']*)?["\']', html):
        local = href.lstrip("/").split("#")[0]
        if local and not os.path.exists(os.path.join(ROOT, local)):
            err(f"{name}: broken internal link -> {href}")


def check_sitemap():
    sm_path = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(sm_path):
        err("sitemap.xml missing")
        return
    tree = ET.parse(sm_path)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {loc.text.strip() for loc in tree.findall(".//s:url/s:loc", ns)}

    expected = set()
    for name in html_files():
        if name in NOINDEX_ALLOWED or name in SKIP_ENTIRELY:
            continue
        path = os.path.join(ROOT, name)
        html = open(path, encoding="utf-8").read()
        robots = get_meta(html, name="robots")
        if robots and "noindex" in robots:
            continue
        expected.add(expected_canonical(name))

    missing = expected - sitemap_urls
    extra = sitemap_urls - expected
    for u in sorted(missing):
        err(f"sitemap.xml: missing entry for indexable page {u}")
    for u in sorted(extra):
        warn(f"sitemap.xml: entry {u} does not correspond to a known indexable page")


def check_duplicates():
    titles = {}
    descs = {}
    for name in html_files():
        if name in NOINDEX_ALLOWED or name in SKIP_ENTIRELY:
            continue
        html = open(os.path.join(ROOT, name), encoding="utf-8").read()
        title_m = re.search(r"<title>(.*?)</title>", html, re.S)
        if title_m:
            titles.setdefault(title_m.group(1).strip(), []).append(name)
        desc = get_meta(html, name="description")
        if desc:
            descs.setdefault(desc, []).append(name)

    for title, pages in titles.items():
        if len(pages) > 1:
            err(f"duplicate <title> {title!r} used on: {', '.join(pages)}")
    for desc, pages in descs.items():
        if len(pages) > 1:
            err(f"duplicate meta description used on: {', '.join(pages)}")


def main():
    for name in html_files():
        check_page(name)
    check_sitemap()
    check_duplicates()

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")

    print(f"\n{len(errors)} error(s), {len(warnings)} warning(s) across "
          f"{len(list(html_files()))} HTML file(s).")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
