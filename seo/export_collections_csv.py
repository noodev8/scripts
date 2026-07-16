"""
SEO: Export Shopify collections to CSV for manual review.
"""

import csv
import os
from list_collections import list_collections

OUT_PATH = os.path.join(os.path.dirname(__file__), "collections.csv")

if __name__ == "__main__":
    cols = list_collections()
    with open(OUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "handle", "products_count", "seo_title", "seo_description"])
        for c in cols:
            writer.writerow([
                c["title"],
                c["handle"],
                c["productsCount"]["count"],
                c["seo"]["title"] or "",
                c["seo"]["description"] or "",
            ])
    print(f"Wrote {len(cols)} collections to {OUT_PATH}")
