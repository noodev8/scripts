"""
SEO priority list A — COLLECTIONS (the traffic play).

Ranked by browse demand not captured. NOT revenue-weighted on purpose — the owner
decides whether a collection is worth working (a high-traffic low-margin one like
mens-goor stays on the list; it's a judgement call, not the report's).

Review cooldown: once you've worked or dismissed a collection, mark it and it drops
off the list for a period, so you don't re-review the same rows every run. State is
in collection_reviews.json (in the repo, so it syncs across machines).

Flags:  IMPROVE = real impressions, weak CTR   STUCK = has products but ~0 impr (invisible)

USAGE:
  python collection_priorities.py                         list (hides snoozed)
  python collection_priorities.py --all                   include snoozed
  python collection_priorities.py --review mens-goor --days 90 --note "low margin"
"""

import argparse, datetime, json, os, sys
import requests
from dotenv import load_dotenv

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from gsc_client import get_service, SITE_URL

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
SHOP, VER = "brookfieldcomfort2", "2025-04"
TARGET_CTR = 0.02
REVIEW_FILE = os.path.join(os.path.dirname(__file__), "collection_reviews.json")
TODAY = datetime.date.today().isoformat()


def load_reviews():
    return json.load(open(REVIEW_FILE)) if os.path.exists(REVIEW_FILE) else {}

def save_reviews(d):
    json.dump(d, open(REVIEW_FILE, "w"), indent=2, sort_keys=True)


def collections():
    tok = os.getenv("SHOPIFY_ACCESS_TOKEN")
    url = f"https://{SHOP}.myshopify.com/admin/api/{VER}/graphql.json"
    q = """query($c:String){collections(first:50,after:$c){edges{node{handle productsCount{count}}}
           pageInfo{hasNextPage endCursor}}}"""
    out, cur = [], None
    while True:
        d = requests.post(url, headers={"X-Shopify-Access-Token": tok},
                          json={"query": q, "variables": {"c": cur}}).json()
        b = d["data"]["collections"]; out += [e["node"] for e in b["edges"]]
        if not b["pageInfo"]["hasNextPage"]: return out
        cur = b["pageInfo"]["endCursor"]


def gsc_by_handle():
    svc = get_service(); end = datetime.date.today() - datetime.timedelta(days=3)
    rows = svc.searchanalytics().query(siteUrl=SITE_URL, body={
        "startDate": (end - datetime.timedelta(days=27)).isoformat(), "endDate": end.isoformat(),
        "dimensions": ["page"], "rowLimit": 25000}).execute().get("rows", [])
    out = {}
    for r in rows:
        u = r["keys"][0]
        if "/collections/" not in u: continue
        h = u.split("/collections/")[1].split("?")[0].split("/")[0].rstrip("/")
        g = out.setdefault(h, {"i": 0, "c": 0, "pw": 0})
        g["i"] += r["impressions"]; g["c"] += r["clicks"]; g["pw"] += r["position"] * r["impressions"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true", help="include snoozed collections")
    ap.add_argument("--review", metavar="HANDLE", help="mark a collection reviewed")
    ap.add_argument("--days", type=int, default=90, help="cooldown days (default 90)")
    ap.add_argument("--note", default="", help="note stored with the review")
    args = ap.parse_args()

    reviews = load_reviews()

    if args.review:
        until = (datetime.date.today() + datetime.timedelta(days=args.days)).isoformat()
        reviews[args.review] = {"reviewed": TODAY, "until": until, "note": args.note}
        save_reviews(reviews)
        print(f"Marked '{args.review}' reviewed — hidden until {until}. Note: {args.note or '-'}")
        return

    cols, gsc = collections(), gsc_by_handle()
    rows = []
    for c in cols:
        h, n = c["handle"], c["productsCount"]["count"]
        g = gsc.get(h, {"i": 0, "c": 0, "pw": 0})
        impr, clk = g["i"], g["c"]
        pos = g["pw"] / impr if impr else 0
        ctr = clk / impr if impr else 0
        gain = impr * max(0, TARGET_CTR - ctr)
        if impr >= 200 and ctr < TARGET_CTR: flag = "IMPROVE"
        elif n >= 4 and impr < 50:           flag = "STUCK"
        else:                                 flag = "ok"
        if flag == "ok" and impr < 200:      continue
        rows.append([h, n, impr, pos, clk, ctr, gain, flag])
    rows.sort(key=lambda r: -r[6])

    snoozed = 0
    shown = []
    for r in rows:
        rv = reviews.get(r[0])
        if rv and rv["until"] > TODAY and not args.all:
            snoozed += 1; continue
        shown.append((r, rv))

    print(f"\nCOLLECTION PRIORITIES — browse demand not captured (GSC 28d)"
          f"{'  [--all: incl. snoozed]' if not args.all else ''}\n")
    print(f"  {'collection':38} {'prod':>4} {'impr':>6} {'pos':>5} {'CTR':>6} {'gain':>5}  {'flag':7} reviewed")
    print("  " + "-" * 92)
    md = [f"# Collection priorities — {TODAY}", "", "Ranked by browse demand not captured (gain = extra clicks/28d at 2% CTR).", "",
          "| collection | prod | impr | pos | CTR | gain | flag | reviewed |", "|---|--:|--:|--:|--:|--:|---|---|"]
    for r, rv in shown[:30]:
        h, n, impr, pos, clk, ctr, gain, flag = r
        rvs = f"til {rv['until']}" + (f" ({rv['note']})" if rv.get('note') else "") if rv else "-"
        print(f"  {h[:38]:38} {n:>4} {impr:>6.0f} {pos or 0:>5.1f} {ctr*100:>5.1f}% "
              f"{gain:>5.0f}  {flag:7} {rvs}")
        md.append(f"| {h} | {n} | {impr:.0f} | {pos or 0:.1f} | {ctr*100:.1f}% | {gain:.0f} | {flag} | {rvs} |")
    md_file = os.path.join(os.path.dirname(__file__), "collection_priorities.md")
    open(md_file, "w", encoding="utf-8").write("\n".join(md) + "\n")
    print(f"\n  gain = extra clicks/28d at {TARGET_CTR*100:.0f}% CTR. "
          f"{snoozed} snoozed (reviewed) hidden — use --all to see. List saved to collection_priorities.md")
    print(f"  Mark one done:  python collection_priorities.py --review <handle> --days 90 --note \"...\"\n")


if __name__ == "__main__":
    main()
