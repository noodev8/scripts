# UKD

Short session guide for working with the UKD supplier channel. Read this first at the start of any UKD session, then ask the user what they want to focus on.

## What UKD is

UKD is a **low-cost, low-margin** supplier. The edge isn't per-unit profit — it's **ease of reordering**. Fast, frictionless restocks let us run these products efficiently even at thin margins.

## Current setup

- **Segment**: `UKD-SEG` (use this to filter UKD products in any query)
- **Primary channel**: Amazon (FBA)
- **Secondary channel**: Shopify, fulfilled from FBA (Multi-Channel Fulfillment) until local-hold volumes justify moving stock in-house
- **Stock location**: Amazon FBA warehouse

## What we do in a UKD session

The goal: **squeeze as much efficient profit as possible** from a thin-margin catalog, without breaking the "easy to reorder" advantage.

Typical session types:

1. **Pricing position review** — where are we vs market, where can we creep up, where are we leaving margin on the table. Start with a summary, then drill in.
2. **New product analysis** — user brings a candidate from UKD; assess likely velocity, margin after FBA fees, competitive position, and whether it fits the UKD-SEG playbook.
3. **Performance check** — which UKD SKUs are earning their shelf space, which aren't, and what to do about the laggards.

## Guiding principles

- **Margin is thin by design** — don't reject a product just because margin looks low; judge on profit-per-reorder-cycle given the low friction.
- **FBA fees matter more here** than on higher-margin lines — always include them in any profitability view.
- **Shopify orders via FBA** are a bridge, not the end state. Watch volume; flag when a SKU looks ready to move to local stock.
- **Reorder ease is the asset** — don't suggest workflows that undermine it (e.g. switching to a slower/cheaper supplier for a few pence).

## Related context

- Amazon pricing conventions: `amz-price/AMZ_PRICING.md`
- Scale / segment work: `scale/CLAUDE_CONTEXT.md`
- Shopify pricing: `shopify-price/README.md`

## How to evolve this file

This README is a living doc. As we learn what works for UKD — pricing rules of thumb, product-selection filters, volume thresholds for moving to local stock — capture it here so the next session picks up where we left off.
