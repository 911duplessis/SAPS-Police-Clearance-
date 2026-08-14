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
  11. robots.txt exists, references the real sitemap.xml, and doesn't
      Disallow any indexable page.
  12. Every indexable page is reachable by following internal links
      starting from index.html (no orphan pages a crawler can't discover).
  13. Every external link resolves with a live HTTP request (warning-only —
      a target site's outage shouldn't fail this required CI check).

Deliberately NOT attempted: a keyword-cannibalization detector. Tried it --
every reasonable title/H1 text heuristic either flags most of the site as
false positives (nearly every page's title legitimately contains "SAPS
Police Clearance" as its brand suffix) or misses the real cases entirely
(the actual cannibalization found 14 Aug 2026 involved pages with no
shared title text at all -- it only showed up in live Semrush ranking
data). Real cannibalization detection needs a live rank-tracking feed
(Search Console or Semrush position data), not static analysis of this
repo. Don't add a fake version of this check just to tick the box.
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
external_links = {}  # url -> [pages that link to it], populated by check_page()


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

    # external links, collected here and checked once (deduplicated) in
    # check_external_links() at the end of the run. Only real <a> links --
    # not <link rel="preconnect">/stylesheet or <script src>, which point
    # at bare origins or asset URLs that were never meant to be fetched as
    # pages and will false-positive as "broken".
    for a_tag in re.findall(r'<a\b[^>]*>', html):
        href_m = re.search(r'href=["\'](https?://[^"\']+)["\']', a_tag)
        if href_m and not href_m.group(1).startswith(DOMAIN):
            external_links.setdefault(href_m.group(1), []).append(name)


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


def check_robots():
    path = os.path.join(ROOT, "robots.txt")
    if not os.path.exists(path):
        err("robots.txt missing")
        return
    text = open(path, encoding="utf-8").read()

    sitemap_line = next((l for l in text.splitlines() if l.strip().lower().startswith("sitemap:")), None)
    if not sitemap_line:
        err("robots.txt: no Sitemap: line")
    elif sitemap_line.split(":", 1)[1].strip() != f"{DOMAIN}/sitemap.xml":
        err(f"robots.txt: Sitemap line {sitemap_line!r} does not point at {DOMAIN}/sitemap.xml")

    disallowed = [
        l.split(":", 1)[1].strip()
        for l in text.splitlines()
        if l.strip().lower().startswith("disallow:") and l.split(":", 1)[1].strip()
    ]
    for name in html_files():
        if name in NOINDEX_ALLOWED or name in SKIP_ENTIRELY:
            continue
        html = open(os.path.join(ROOT, name), encoding="utf-8").read()
        robots_meta = get_meta(html, name="robots")
        if robots_meta and "noindex" in robots_meta:
            continue
        for d in disallowed:
            if d.rstrip("*") and (f"/{name}").startswith(d.rstrip("*")):
                err(f"robots.txt: Disallow {d!r} blocks indexable page {name}")


def check_orphans():
    """Every indexable page should be reachable by following internal links
    from index.html — otherwise a crawler relying on link discovery (rather
    than only the sitemap) may never find it."""
    graph = {}
    for name in html_files():
        if name in SKIP_ENTIRELY:
            continue
        html = open(os.path.join(ROOT, name), encoding="utf-8").read()
        links = set()
        for href in re.findall(r'href=["\'](/[a-zA-Z0-9_\-./]+\.html)(?:#[^"\']*)?["\']', html):
            local = href.lstrip("/").split("#")[0]
            if local:
                links.add(local)
        graph[name] = links

    if "index.html" not in graph:
        return
    seen = {"index.html"}
    queue = ["index.html"]
    while queue:
        cur = queue.pop()
        for nxt in graph.get(cur, ()):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)

    for name in html_files():
        if name in NOINDEX_ALLOWED or name in SKIP_ENTIRELY:
            continue
        html = open(os.path.join(ROOT, name), encoding="utf-8").read()
        robots_meta = get_meta(html, name="robots")
        if robots_meta and "noindex" in robots_meta:
            continue
        if name not in seen:
            err(f"{name}: orphan page — unreachable by internal links from index.html")


def check_external_links():
    """Live HTTP check on every external link collected by check_page().

    Deliberately warning-only, never error-level: this is a required CI
    check gating merges, and a government site having a bad five minutes
    shouldn't block an unrelated PR. Best-effort — network problems in the
    CI environment itself (not the target site) are reported once and
    skipped rather than spamming a warning per link.
    """
    import urllib.request
    import urllib.error

    if not external_links:
        return

    network_failures = 0
    for url, pages in sorted(external_links.items()):
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Mozilla/5.0 (seo_check.py link checker)"})
        try:
            with urllib.request.urlopen(req, timeout=8) as resp:
                status = resp.status
        except urllib.error.HTTPError as e:
            status = e.code
        except Exception:
            # Some servers reject HEAD outright; retry with GET before giving up.
            try:
                req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0 (seo_check.py link checker)"})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    status = resp.status
            except urllib.error.HTTPError as e:
                status = e.code
            except Exception:
                network_failures += 1
                if network_failures > 5:
                    warn("external link check: too many network-level failures — CI environment may lack outbound access, skipping the rest")
                    return
                warn(f"external link unreachable (network error): {url} — linked from {', '.join(pages)}")
                continue
        if status >= 400:
            warn(f"external link returned HTTP {status}: {url} — linked from {', '.join(pages)}")


def main():
    for name in html_files():
        check_page(name)
    check_sitemap()
    check_duplicates()
    check_robots()
    check_orphans()
    check_external_links()

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
