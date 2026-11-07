"""
SEO priority list B — PRODUCTS (the value play).

Product-intent search is uniformly LOW, so volume can't be the ranker. A page built
once earns for years free, so rank by VALUE:
  - proven:    organic revenue + conversion % (GA4)
  - potential: units x gross margin (profit weight)
Shown only where there's product-intent search to capture and room to rank (pos>5).

Birkenstock only — Shopify-win by default (no Amazon conflict). Parked products
(e.g. St Ives, priced high to protect Amazon) are excluded by brand.

Review cooldown: mark a product worked/dismissed and it drops off for a period.
State in product_reviews.json (repo, syncs across machines). The list is also
written to product_priorities.md so you can just open it.

USAGE:
  python product_priorities.py                       list (hides snoozed) + writes .md
  python product_priorities.py --all                 include snoozed
  python product_priorities.py --review <handle> --days 90 --note "done"
"""

import argparse, datetime, json, os, sys
import psycopg2

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\scripts"); sys.path.insert(0, r"C:\scripts\seo")
from logging_utils import get_db_config
from gsc_client import get_service, SITE_URL
from ga4_client import run_report

REVIEW_FILE = os.path.join(os.path.dirname(__file__), "product_reviews.json")
MD_FILE = os.path.join(os.path.dirname(__file__), "product_priorities.md")
TODAY = datetime.date.today().isoformat()

COLOUR = {"brown","black","white","blue","navy","khaki","tan","pink","green","grey","gray",
          "red","patent","nubuck","suede","oiled","dark","taupe","stone","mocha","sand",
          "beige","gold","silver","rose","cream","olive","anthracite","eva","graphite"}
BROWSE = {"trainers","sandals","sliders","sneakers","clogs","shoes","slippers","sandal"}
def intent(q):
    t = set((q or "").lower().replace("'", "").split())
    if (t & BROWSE) and not (t & COLOUR): return "browse"
    return "product" if (t & COLOUR) else "browse"

def h_of(u): return u.split("/products/")[-1].split("?")[0].split("/")[0].rstrip("/")
def load_reviews(): return json.load(open(REVIEW_FILE)) if os.path.exists(REVIEW_FILE) else {}
def save_reviews(d): json.dump(d, open(REVIEW_FILE, "w"), indent=2, sort_keys=True)


def build_rows():
    with psycopg2.connect(**get_db_config()) as c, c.cursor() as cur:
        cur.execute("""
            SELECT ss.handle, SUM(s.qty),
                   AVG(NULLIF(ss.shopifyprice,'')::numeric - NULLIF(ss.cost,'')::numeric)
            FROM sales s JOIN skusummary ss ON ss.groupid = s.groupid
            WHERE s.channel='SHP' AND s.solddate >= %s AND ss.brand='Birkenstock'
                  AND ss.handle IS NOT NULL AND ss.handle <> ''
            GROUP BY ss.handle""", (datetime.date.today() - datetime.timedelta(days=365),))
        prod = {h: {"units": u, "margin": float(m or 0)} for h, u, m in cur.fetchall()}

    svc = get_service(); end = datetime.date.today() - datetime.timedelta(days=3)
    gsc, topq = {}, {}
    for r in svc.searchanalytics().query(siteUrl=SITE_URL, body={
            "startDate": (end - datetime.timedelta(days=27)).isoformat(), "endDate": end.isoformat(),
            "dimensions": ["page", "query"], "rowLimit": 25000}).execute().get("rows", []):
        u, q = r["keys"]
        if "/products/" not in u: continue
        h = h_of(u); g = gsc.setdefault(h, {"i": 0, "c": 0, "pw": 0})
        g["i"] += r["impressions"]; g["c"] += r["clicks"]; g["pw"] += r["position"] * r["impressions"]
        if r["impressions"] > topq.get(h, (0, None))[0]: topq[h] = (r["impressions"], q)

    ga = {}
    for r in run_report(["landingPage"], ["sessions", "ecommercePurchases", "totalRevenue"],
                        "90daysAgo", "yesterday", filter_dim="sessionDefaultChannelGroup",
                        filter_value="Organic Search"):
        if "/products/" in (r["landingPage"] or ""):
            ga[h_of(r["landingPage"])] = {"s": r["sessions"], "b": r["ecommercePurchases"], "r": r["totalRevenue"]}

    rows = []
    for h, p in prod.items():
        g = gsc.get(h)
        if not g or g["i"] < 10: continue
        pos = g["pw"] / g["i"]
        if intent(topq.get(h, (0, ""))[1]) != "product" or pos <= 5: continue
        a = ga.get(h, {"s": 0, "b": 0, "r": 0})
        conv = a["b"] / a["s"] * 100 if a["s"] else 0
        rows.append([h, p["units"], p["margin"], p["units"] * p["margin"], conv, a["r"], g["i"], pos])
    rows.sort(key=lambda r: (-r[5], -r[3]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--review", metavar="HANDLE")
    ap.add_argument("--days", type=int, default=90)
    ap.add_argument("--note", default="")
    args = ap.parse_args()

    reviews = load_reviews()
    if args.review:
        until = (datetime.date.today() + datetime.timedelta(days=args.days)).isoformat()
        reviews[args.review] = {"reviewed": TODAY, "until": until, "note": args.note}
        save_reviews(reviews)
        print(f"Marked '{args.review}' reviewed — hidden until {until}. Note: {args.note or '-'}")
        return

    rows = build_rows()
    shown, snoozed = [], 0
    for r in rows:
        rv = reviews.get(r[0])
        if rv and rv["until"] > TODAY and not args.all:
            snoozed += 1; continue
        shown.append((r, rv))

    hdr = f"{'product':42} {'un':>3} {'u×m':>6} {'conv%':>6} {'org£':>5} {'impr':>5} {'pos':>5}  reviewed"
    print(f"\nPRODUCT PRIORITIES — Birkenstock, ranked by value (units/margin 12m, GSC 28d, GA4 90d)\n")
    print("  " + hdr); print("  " + "-" * 96)
    md = [f"# Product priorities — {TODAY}", "", "Ranked by value (proven organic £, then units×margin).", "",
          "| product | units | u×m | conv% | org£ | impr | pos | reviewed |", "|---|--:|--:|--:|--:|--:|--:|---|"]
    for r, rv in shown[:30]:
        h, un, mgn, pot, conv, orgr, impr, pos = r
        rvs = f"til {rv['until']}" + (f" ({rv['note']})" if rv.get('note') else "") if rv else "-"
        print(f"  {h[:42]:42} {un:>3.0f} {pot:>6.0f} {conv:>5.0f}% {orgr:>5.0f} {impr:>5.0f} {pos:>5.1f}  {rvs}")
        md.append(f"| {h} | {un:.0f} | {pot:.0f} | {conv:.0f}% | £{orgr:.0f} | {impr:.0f} | {pos:.1f} | {rvs} |")
    print(f"\n  {snoozed} snoozed (reviewed) hidden — use --all to see. List saved to product_priorities.md")
    print(f"  Mark one done:  python product_priorities.py --review <handle> --days 90 --note \"...\"\n")
    open(MD_FILE, "w", encoding="utf-8").write("\n".join(md) + "\n")


if __name__ == "__main__":
    main()
