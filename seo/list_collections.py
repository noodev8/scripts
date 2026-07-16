"""
SEO: List Shopify collections

Quick check that the Shopify Admin API can return collection names/handles,
as a starting point for SEO work (title/meta review per collection, etc).

USAGE:
• python list_collections.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

SHOP_NAME = "brookfieldcomfort2"
API_VERSION = "2025-04"
ACCESS_TOKEN = os.getenv('SHOPIFY_ACCESS_TOKEN')

if not ACCESS_TOKEN:
    raise ValueError("SHOPIFY_ACCESS_TOKEN not found in .env file")


def list_collections():
    url = f"https://{SHOP_NAME}.myshopify.com/admin/api/{API_VERSION}/graphql.json"
    headers = {
        "X-Shopify-Access-Token": ACCESS_TOKEN,
        "Content-Type": "application/json"
    }

    query = """
    query($cursor: String) {
        collections(first: 50, after: $cursor) {
            edges {
                node {
                    id
                    title
                    handle
                    productsCount { count }
                    seo { title description }
                }
            }
            pageInfo { hasNextPage endCursor }
        }
    }
    """

    collections = []
    cursor = None
    while True:
        resp = requests.post(url, headers=headers, json={"query": query, "variables": {"cursor": cursor}})
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise RuntimeError(data["errors"])

        block = data["data"]["collections"]
        for edge in block["edges"]:
            collections.append(edge["node"])

        if block["pageInfo"]["hasNextPage"]:
            cursor = block["pageInfo"]["endCursor"]
        else:
            break

    return collections


if __name__ == "__main__":
    cols = list_collections()
    print(f"Found {len(cols)} collections:\n")
    for c in cols:
        seo_title = c["seo"]["title"] or "(none)"
        print(f"- {c['title']}  [handle={c['handle']}, products={c['productsCount']['count']}, seo_title={seo_title}]")
