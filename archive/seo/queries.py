"""
SEO: the keyword miner. What we rank for, and what has no page to rank with.

GSC is a mirror, not a market: it only reports queries we ALREADY appear for, so
this finds demand where we have a footing and is blind to greenfield. That limit
is the point -- everything it surfaces is proven demand on proven authority.

The default view looks for the Arizona pattern. When a browse query has no page
built for it, Google does not decline to rank us; it scatters the query across
whatever product pages it can find, each earning a few impressions and no clicks.
So a term with volume, spread across many pages, with no collection among them,
is a page waiting to be built. That is how /collections/birkenstock-arizona was
found: 2,441 impressions, 43 pages, no collection, 15 clicks.

USAGE:
• python queries.py                     (clusters: what has volume and no page)
• python queries.py --page /pages/x     (what one page ranks for)
• python queries.py --query "arizona birkenstock"   (what ranks for one term)
• python queries.py --contains narrow   (every query containing a word)
"""

import argparse
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from gsc_client import get_service, SITE_URL

GSC_LAG_DAYS = 3
WINDOW_DAYS = 28
SITE_ROOT = SITE_URL.rstrip("/")
MIN_CLUSTER_IMPR = 200
MIN_SPREAD = 5  # pages a term must be scattered over to count as having no page

# Words that carry no intent of their own. Two kinds are here for reasons worth
# keeping: the supplier brand, because it is in nearly every query and would just
# produce one useless bucket; and OUR name, because "brookfield"/"comfort" are
# navigational -- people already looking for us, served by the homepage at
# position 3. They are not a page to build. Fit and style words are deliberately
# NOT here: "narrow", "arizona" and "zermatt" are exactly what we are hunting.
STOP = {
    "birkenstock", "birkenstocks",
    "brookfield", "comfort",
    "uk", "the", "a", "an", "for", "in", "of", "and", "or", "to", "my", "me",
    "is", "are", "do", "does", "dont", "not", "why", "what", "how",
    "with", "on", "at", "buy", "online", "shop", "sale", "cheap", "best",
}


def tokens(q):
    """Intent-carrying words in a query. Digits are dropped -- sizes like '260'
    are real searches but cluster into noise rather than a page anyone can build.
    Apostrophes are stripped so "women's" and "womens" are one term, not two."""
    out = []
    for w in re.split(r"[^a-z0-9]+", q.lower().replace("'", "")):
        if w and w not in STOP and not w.isdigit() and len(w) > 2:
            out.append(w)
    return set(out)


def fetch(service, dims, filters=None):
    end = datetime.date.today() - datetime.timedelta(days=GSC_LAG_DAYS)
    body = {
        "startDate": (end - datetime.timedelta(days=WINDOW_DAYS - 1)).isoformat(),
        "endDate": end.isoformat(),
        "dimensions": dims,
        "rowLimit": 25000,
    }
    if filters:
        body["dimensionFilterGroups"] = [{"filters": filters}]
    rows = service.searchanalytics().query(siteUrl=SITE_URL, body=body).execute()
    return rows.get("rows", []), end


def to_url(s):
    """Accept a full URL, a path, or a Git Bash-mangled path.

    MSYS rewrites a leading-slash argument into a Windows path, so
    "--page /collections/x" arrives as "C:/Program Files/Git/collections/x".
    Every Shopify URL carries one of these markers, so recovering from the marker
    onward survives the mangling instead of silently querying a nonsense URL and
    reporting zero rows.
    """
    if s.startswith("http"):
        return s
    for marker in ("/collections/", "/pages/", "/products/", "/blogs/"):
        if marker in s:
            return SITE_ROOT + s[s.index(marker):]
    return SITE_ROOT + (s if s.startswith("/") else "/" + s)


def short(url, width=44):
    return (url.replace(SITE_ROOT, "") or "/")[:width]


def ctr(clicks, impr):
    return clicks / impr * 100 if impr else 0


def print_queries(rows, title, width=50):
    print(f"\n{'=' * 78}\n{title}\n{'=' * 78}")
    print(f"  {'query':{width}} {'clicks':>6} {'impr':>7} {'CTR':>6} {'pos':>5}")
    for r in rows:
        print(f"  {r['keys'][0][:width]:{width}} {r['clicks']:>6,.0f} {r['impressions']:>7,.0f} "
              f"{ctr(r['clicks'], r['impressions']):>5.2f}% {r['position']:>5.1f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--page", help="what one page ranks for (path or full URL)")
    ap.add_argument("--query", help="what pages rank for one term")
    ap.add_argument("--contains", help="every query containing a word")
    ap.add_argument("--top", type=int, default=25, help="rows (default 25)")
    args = ap.parse_args()

    service = get_service()

    # ---- what one page ranks for ----
    if args.page:
        url = to_url(args.page)
        rows, end = fetch(service, ["query"],
                          [{"dimension": "page", "operator": "equals", "expression": url}])
        c = sum(r["clicks"] for r in rows)
        i = sum(r["impressions"] for r in rows)
        print(f"\n{short(url, 70)} - {WINDOW_DAYS}d to {end}")
        print(f"{len(rows):,} named queries, {c:,.0f} clicks, {i:,.0f} impressions")
        print("GSC anonymises rare queries, so this will NOT sum to the page total.")
        print_queries(sorted(rows, key=lambda r: -r["impressions"])[:args.top],
                      "BY IMPRESSIONS")
        print_queries(sorted(rows, key=lambda r: -r["clicks"])[:args.top],
                      "BY CLICKS - what actually earns")
        print()
        return

    # ---- what ranks for one term ----
    if args.query:
        rows, end = fetch(service, ["page"],
                          [{"dimension": "query", "operator": "equals", "expression": args.query}])
        print(f"\n\"{args.query}\" - {WINDOW_DAYS}d to {end} - {len(rows)} pages ranking\n")
        print(f"  {'page':56} {'clicks':>6} {'impr':>7} {'pos':>5}")
        for r in sorted(rows, key=lambda r: -r["impressions"])[:args.top]:
            print(f"  {short(r['keys'][0], 56):56} {r['clicks']:>6,.0f} "
                  f"{r['impressions']:>7,.0f} {r['position']:>5.1f}")
        if len(rows) > 5:
            print(f"\n  {len(rows)} pages splitting one query is the no-dedicated-page")
            print("  signal - Google is guessing because nothing was built for this.")
        print()
        return

    # ---- every query containing a word ----
    if args.contains:
        rows, end = fetch(service, ["query"])
        m = [r for r in rows if args.contains.lower() in r["keys"][0].lower()]
        c = sum(r["clicks"] for r in m)
        i = sum(r["impressions"] for r in m)
        print(f"\n\"{args.contains}\" - {WINDOW_DAYS}d to {end} - {len(m)} queries, "
              f"{c:,.0f} clicks, {i:,.0f} impressions, {ctr(c, i):.2f}% CTR")
        print_queries(sorted(m, key=lambda r: -r["impressions"])[:args.top], "BY IMPRESSIONS")
        print()
        return

    # ---- default: clusters with volume and no page ----
    rows, end = fetch(service, ["query", "page"])

    clusters = {}
    for r in rows:
        q, page = r["keys"]
        for t in tokens(q):
            c = clusters.setdefault(t, {"queries": set(), "clicks": 0, "impr": 0,
                                        "posw": 0, "pages": {}})
            c["queries"].add(q)
            c["clicks"] += r["clicks"]
            c["impr"] += r["impressions"]
            c["posw"] += r["position"] * r["impressions"]
            c["pages"][page] = c["pages"].get(page, 0) + r["impressions"]

    big = {t: c for t, c in clusters.items() if c["impr"] >= MIN_CLUSTER_IMPR}

    print(f"\nQUERY CLUSTERS - {WINDOW_DAYS}d to {end} - terms over "
          f"{MIN_CLUSTER_IMPR} impressions")
    print("A query counts toward every token it contains, so columns do not sum "
          "to site totals.\n")
    print("=" * 78)
    print(f"  {'term':14} {'queries':>7} {'impr':>7} {'clicks':>6} {'CTR':>6} "
          f"{'pos':>5} {'pages':>6}  {'collection':24}")
    print("=" * 78)

    rank = sorted(big.items(), key=lambda kv: -kv[1]["impr"])
    todo = []
    # Scan every cluster, print only --top of them: discovery must not depend on
    # how many rows someone asked to see. Arizona sits at rank 12.
    for n, (t, c) in enumerate(rank):
        # A collection OR an info page whose slug carries the term is the page
        # built for it -- the size guide owns "size" even though it is a /pages/.
        # Product pages containing the word do not count: 143 Arizona product
        # pages is the symptom, not the cure.
        owned = [p for p in c["pages"]
                 if ("/collections/" in p or "/pages/" in p) and t in p.rsplit("/", 1)[-1]]
        best = max(owned, key=lambda p: c["pages"][p]) if owned else None
        owner = short(best, 24).replace("/collections/", "").replace("/pages/", "") \
            if best else "NONE  <-- no page"
        # Spread is what separates "no page exists" from "a page exists and ranks
        # badly". Google scattering a term over many pages means it found nothing
        # built for it; two pages means it knows the answer and rates it poorly,
        # which is a ranking job the CTR curve already covers.
        if not best and len(c["pages"]) >= MIN_SPREAD:
            todo.append((t, c))
        if n < args.top:
            print(f"  {t[:14]:14} {len(c['queries']):>7} {c['impr']:>7,.0f} {c['clicks']:>6,.0f} "
                  f"{ctr(c['clicks'], c['impr']):>5.2f}% {c['posw'] / c['impr']:>5.1f} "
                  f"{len(c['pages']):>6}  {owner:24}")

    print()
    print("=" * 78)
    print("NO PAGE BUILT FOR IT - volume, scattered across pages, no collection")
    print("=" * 78)
    if not todo:
        print("  Nothing. Every term with volume has a collection serving it.")
    for t, c in sorted(todo, key=lambda kv: -kv[1]["impr"])[:10]:
        top = max(c["pages"], key=lambda p: c["pages"][p])
        print(f"  {t:14} {c['impr']:>7,.0f} impr  {c['clicks']:>4,.0f} clicks  "
              f"pos {c['posw'] / c['impr']:>4.1f}  across {len(c['pages'])} pages")
        print(f"                 best is {short(top, 56)}")
    print()
    print(f"  Volume + spread over {MIN_SPREAD}+ pages + no page named for it = build it.")
    print("  Terms above with NONE but few pages are a ranking problem, not a")
    print("  missing page - a page serves them, just not one named for the term.")
    print("  Check --query \"<term>\" before acting: position is averaged across")
    print("  every query, and a term can be spread over pages legitimately.\n")


if __name__ == "__main__":
    main()
