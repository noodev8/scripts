# amz-match — Shopify "match Amazon price"

Self-contained cron job that pins the Shopify price of **chosen styles** to Amazon's cheapest **in-stock** size.

## The rule

For every style flagged `skusummary.match_amazon_price = true`:

```
shopifyprice  =  MIN(amzfeed.amzprice)   over that groupid's rows WHERE amzlive > 0
```

Amazon is the **ceiling** ("never higher than Amazon lowest") — Shopify stays competitive and Amazon is never undercut by omission. Zero admin on the chosen few.

Source of truth is **`amzfeed`** (Amazon's own price, refreshed when the operator loads the Amazon file each late morning). Reconciling off `amzfeed` — rather than off "the moment someone edits Amazon" — means it also catches changes made **outside our tools** (Seller Central by hand, or a repricer). `amzfeed` is **read-only** here.

## Behaviour per style

| Situation | Action |
|---|---|
| No in-stock Amazon size (`amzlive>0` gives nothing) | **skip** — `no_amazon_stock` |
| Amazon lowest `< cost` | **skip** — `below_cost` (never sell Shopify at a loss) |
| Amazon lowest already equals Shopify price | **no-op** — no DB write, no API call |
| Otherwise | **change** — update `shopifyprice`, log `price_change_log` (`changed_by = 'Amazon match (auto)'`), push Shopify + Google |

Above-RRP is **allowed** (flagged in the log), same as the manual Apply (W1).

A run where nothing changed (weekend / operator too busy / Amazon didn't move) is a near-instant **no-op that hits no external API** — the diff-guard only pushes a style whose Amazon-lowest actually differs. Safe to run daily.

## Push & failure handling

- **Shopify**: per-variant REST price update (same as `../price_update.py`). If the direct push fails, the row is flagged `shopifychange = 1` so the **nightly `price_update.py` sweep** re-pushes it (no operator watches an automated run).
- **Google**: per-`googleid` Content API update. A miss self-heals via tonight's `merchant_feed.py --upload` (regenerates the whole feed from the DB), so no flag is needed.

## Enabling a style

Until the bcweb drill toggle lands, enable/disable with SQL:

```sql
UPDATE skusummary SET match_amazon_price = true  WHERE groupid = 'ABC123';   -- opt in
UPDATE skusummary SET match_amazon_price = false WHERE groupid = 'ABC123';   -- opt out
SELECT groupid FROM skusummary WHERE match_amazon_price = true;              -- who's on
```

Requires the column — see `bcweb/bcweb-server/migrations/20260719_skusummary_match_amazon_price.sql`.

## Running

```
python amz_match_sync.py            # live reconcile of every flagged style
python amz_match_sync.py --dry-run  # log what WOULD change; no DB write, no push  (run this first)
python amz_match_sync.py --groupid ABC123
python amz_match_sync.py --no-google
```

Logs: `../logs/amz_match_sync.log` (shared logging, same as every other script).

## Schedule

`crontab.txt` — twice each afternoon after the amzfeed refresh (times are GMT = BST − 1):

```
0 13,16 * * * /apps/scripts/venv/bin/python /apps/scripts/amz-match/amz_match_sync.py
```
= **14:00 & 17:00 BST**. The 17:00 run costs nothing on days the 14:00 run already synced (idempotent no-op), so it just covers days the operator loads the feed late.

## Shared dependencies (reused from `C:\scripts`, not duplicated)

`logging_utils.py`, `.env` (`DB_*`, `SHOPIFY_ACCESS_TOKEN`), and the Google service-account JSON. Retires as a unit: delete this folder + the crontab line when the legacy PowerBuilder app (and its manual amzfeed refresh) goes.
