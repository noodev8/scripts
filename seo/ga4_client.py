"""
SEO: Google Analytics 4 Data API client helper.

Uses the same merchant-feed-api-462809 service account as gsc_client.py, granted
Viewer on the GA4 property 2026-07-17. GA4 is the missing attribution layer: it
splits sessions and revenue by traffic source, so organic can finally be told
apart from paid.

Caveats baked into how this is read (see seo/README.md):
- GA4 undercounts absolute revenue (~60% of the sales table: consent, ad-blockers,
  cross-device). Trust the split between channels, never the absolute pounds.
- "Organic Search" includes brand searches SEO did not earn. Organic revenue
  overstates incremental SEO. GSC can split brand vs non-brand.
"""

import os
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange, Dimension, Metric, RunReportRequest,
    Filter, FilterExpression, OrderBy,
)

SCRIPT_DIR = os.path.dirname(__file__)
KEY_PATH = os.path.join(SCRIPT_DIR, "..", "merchant-feed-api-462809-23c712978791.json")
SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

# GA4 property: brookfieldcomfort - GA4 (account Brookfield Comfort, 84449502)
PROPERTY_ID = "312199890"


def get_client():
    creds = service_account.Credentials.from_service_account_file(KEY_PATH, scopes=SCOPES)
    return BetaAnalyticsDataClient(credentials=creds)


def run_report(dimensions, metrics, start, end, filter_dim=None, filter_value=None,
               order_metric=None, limit=25000):
    """Run a GA4 report. dimensions/metrics are lists of API names.

    filter_dim/filter_value apply a server-side exact-match dimension filter
    (e.g. sessionDefaultChannelGroup == "Organic Search"). order_metric sorts
    descending by that metric. Returns a list of dicts keyed by dimension +
    metric name, metrics cast to float.
    """
    client = get_client()
    kwargs = dict(
        property=f"properties/{PROPERTY_ID}",
        dimensions=[Dimension(name=d) for d in dimensions],
        metrics=[Metric(name=m) for m in metrics],
        date_ranges=[DateRange(start_date=start, end_date=end)],
        limit=limit,
    )
    if filter_dim and filter_value is not None:
        kwargs["dimension_filter"] = FilterExpression(
            filter=Filter(
                field_name=filter_dim,
                string_filter=Filter.StringFilter(value=filter_value),
            )
        )
    if order_metric:
        kwargs["order_bys"] = [OrderBy(
            metric=OrderBy.MetricOrderBy(metric_name=order_metric), desc=True)]
    resp = client.run_report(RunReportRequest(**kwargs))
    out = []
    for row in resp.rows:
        rec = {}
        for i, d in enumerate(dimensions):
            rec[d] = row.dimension_values[i].value
        for i, m in enumerate(metrics):
            rec[m] = float(row.metric_values[i].value or 0)
        out.append(rec)
    return out


if __name__ == "__main__":
    # Access test: reproduce the channel-group revenue split we read off the
    # screenshots (last 90 days). If this prints rows, the grant worked.
    rows = run_report(
        ["sessionPrimaryChannelGroup"],
        ["sessions", "totalRevenue"],
        "90daysAgo", "yesterday",
    )
    rows.sort(key=lambda r: -r["totalRevenue"])
    print(f"GA4 property {PROPERTY_ID} - last 90 days - access OK\n")
    print(f"  {'channel':22} {'sessions':>9} {'revenue':>11} {'£/sess':>8}")
    for r in rows:
        s, rev = r["sessions"], r["totalRevenue"]
        per = rev / s if s else 0
        print(f"  {r['sessionPrimaryChannelGroup']:22} {s:>9,.0f} "
              f"{rev:>10,.0f} {per:>8.2f}")
