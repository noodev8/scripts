"""
SEO: List products inside a given Shopify collection (by handle).

USAGE:
• python check_collection_products.py boulevard boulevard-shoes
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

URL = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"
HEADERS = {"X-Shopify-Access-Token": ACCESS_TOKEN, "Content-Type": "application/json"}


def products_in_collection(handle):
    query = """
    query($handle: String!) {
        collectionByHandle(handle: $handle) {
            title
            products(first: 100) {
                edges { node { title productType } }
            }
        }
    }
    """
    resp = requests.post(URL, headers=HEADERS, json={"query": query, "variables": {"handle": handle}})
    resp.raise_for_status()
    data = resp.json()
    return data["data"]["collectionByHandle"]


if __name__ == "__main__":
    for handle in sys.argv[1:]:
        col = products_in_collection(handle)
        if not col:
            print(f"{handle}: not found")
            continue
        print(f"\n{col['title']} [{handle}] — {len(col['products']['edges'])} products:")
        for e in col["products"]["edges"]:
            print(f"  - {e['node']['title']}  ({e['node']['productType']})")
