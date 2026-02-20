# Google Ads Stock Track

Records daily stock levels and imports Google Ads spend into the `google_stock_track` table.

## Run

```
python C:\scripts\google-ads-stocktrack\update_google_stock_track.py
```

Safe to re-run — skips if yesterday's snapshot already exists.

## Google Ads CSV

To import ad spend data, export a 30-day report from Google Ads and save it as `adcost_summary_30.csv` in this folder before running.
