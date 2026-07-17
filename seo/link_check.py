"""
SEO hygiene: what internal pages link to a collection, before deleting it.

Crawls the live storefront's collections + pages + blogs + home and builds a
reverse map of every internal /collections/ link. The nav/footer is on every
page, so it is captured automatically -- if a handle is linked from most pages,
it is in the menu (the dangerous case). Products are not crawled: a product
description linking to an obscure collection is very rare.

Pairs with thin_collections.py (finds delete candidates) and the delete rule in
seo/CHANGELOG.md: a dead page with no traffic and no links should just be
deleted (clean 404), not redirected -- there is no equity to preserve.

USAGE:
• python link_check.py mens-wedding-shoes nhs-care     (check these handles)
• python link_check.py --file handles.txt              (one handle per line)
"""

import argparse
import re
import sys
import time

import requests

sys.stdout.reconfigure(encoding="utf-8")

ROOT = "https://brookfieldcomfort.com"
LOC = re.compile(r"<loc>([^<]+)</loc>")
HREF = re.compile(r'href=["\']([^"\']*?/collections/[^"\']*?)["\']', re.I)

S = requests.Session()
S.headers["User-Agent"] = "Mozilla/5.0 (link-check; brookfieldcomfort internal)"


def get(url):
    try:
        r = S.get(url, timeout=20)
        if r.status_code == 200:
            return r.text
        print(f"  ! {url} -> HTTP {r.status_code}", file=sys.stderr)
    except Exception as e:
        print(f"  ! {url} -> {e}", file=sys.stderr)
    return ""


def sitemap_urls():
    """Collection, page and blog-article URLs from the sitemap (skip products)."""
    index = get(f"{ROOT}/sitemap.xml")
    subs = [u for u in LOC.findall(index)
            if any(k in u for k in ("collections", "pages", "blogs"))]
    urls = set()
    for sm in subs:
        for u in LOC.findall(get(sm)):
            if not u.endswith(".xml"):
                urls.add(u.split("?")[0])
    return urls


def handle_of(href):
    if "/collections/" not in href:
        return None
    return href.split("/collections/")[1].split("?")[0].split("#")[0].split("/")[0].rstrip("/").lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("handles", nargs="*", help="collection handles to check")
    ap.add_argument("--file", help="file with one handle per line")
    args = ap.parse_args()

    targets = [h.strip().lower() for h in args.handles]
    if args.file:
        with open(args.file) as f:
            targets += [ln.strip().lower() for ln in f if ln.strip()]
    if not targets:
        ap.error("give at least one handle (positional or --file)")

    pages = sitemap_urls()
    pages.add(ROOT + "/")
    print(f"Crawling {len(pages)} pages (collections + pages + blogs + home)...\n")

    inbound = {t: {} for t in targets}
    crawled = 0
    for url in sorted(pages):
        html = get(url)
        if not html:
            continue
        crawled += 1
        src = handle_of(url) if "/collections/" in url else (url.replace(ROOT, "") or "/")
        for href in HREF.findall(html):
            h = handle_of(href)
            if h in inbound and h != src:  # ignore self-links (pagination)
                label = url.replace(ROOT, "") or "/"
                inbound[h][label] = inbound[h].get(label, 0) + 1
        time.sleep(0.05)

    coverage = crawled / len(pages) if pages else 0
    print(f"Crawled {crawled} of {len(pages)} pages ({coverage:.0%}).\n")
    if coverage < 0.7:
        print("  ⚠ INCOMPLETE CRAWL -- most fetches failed, likely Shopify rate-")
        print("    limiting (503) after repeated runs. A 'no links' result here is")
        print("    NOT trustworthy: a nav link could sit on an un-fetched page. Wait")
        print("    a few minutes and re-run before acting on this.\n")
    nav_threshold = max(2, int(crawled * 0.5))  # linked from >50% ~= nav/footer
    for t in targets:
        srcs = inbound[t]
        if not srcs:
            print(f"  OK   {t}  -- no internal links. Safe to delete (clean 404).")
        else:
            tag = "IN NAV/FOOTER" if len(srcs) >= nav_threshold else "LINKED"
            print(f"  {tag}  {t}  ({len(srcs)} source page(s)):")
            for label in sorted(srcs)[:10]:
                print(f"         <- {label}")
            if len(srcs) > 10:
                print(f"         ... and {len(srcs) - 10} more")
    print("\n  Note: products not crawled; 24-ish sitemap URLs may not respond.")
    print("  For a page with real traffic/links, redirect to a relevant parent;")
    print("  for a dead page, a clean 404 is correct. See seo/CHANGELOG.md.\n")


if __name__ == "__main__":
    main()
