# email/ — LEGACY (2026-09-21)

**Email marketing is now bcweb work. Don't start anything new here.**

The files in this folder stay put — `EMAIL_STRATEGY.md`, `CAMPAIGN_3_BRIEF.md`,
`KLAVIYO_MCP_SETUP.md` and `design/` are the record of the Klaviyo programme and
remain the reference for it. Nothing has been moved or copied anywhere.

## What changed

Klaviyo has been **switched off**. Email is being restarted as a bcweb concern
(owner, 2026-09-21) — the audience logic is segments, dead stock and size curves,
which live in bcweb and `brookfield_prod` already. Nothing exists in bcweb yet.

## Why the old programme is not the template

Twelve months of Klaviyo produced 13 orders / GBP 858. Of that, the automated
flows (abandoned checkout, browse abandonment) were 11 orders / GBP 748; the eight
manual campaigns were 2 orders / GBP 110.

The campaigns went to lapsed Birkenstock repurchasers and the suppression list
explicitly excluded "No Birkenstock orders" — i.e. the roughly 6,000 people on a
~10,000 list who have never bought. Birkenstock has a multi-year replacement
cycle, so the 8.3% repeat rate looks closer to a ceiling than a fault. The flows
are the part that worked and the part worth rebuilding.

Campaign 3 was designed (`design/*Birkenstock 3.png`, 2026-04-10) but its results
were never logged here. They are still inside Klaviyo and will be lost when that
account lapses — export before it does.

The design learnings in `EMAIL_STRATEGY.md` still hold (short curious subject,
personal tone, 1-2 hero products, always set preview text). Only the audience
thesis changed.

## Replacement tool

**Spoks** is under evaluation — docs.spoks.com / api.spoks.com, API-key auth,
60 requests/minute, beta. Its Shopify sync to `brookfieldcomfort2` is already
complete. **Nothing is decided.** The open question is whether it can segment on
"has never purchased".

Any Spoks credential belongs in `bcweb-server\.env`, not this repo's `.env`.

## If a cron job is ever needed

A scheduled contact/tag sync is the one piece that could legitimately land back
in this repo, since unattended jobs live here and `crontab.txt` is authoritative
for schedules. Not decided. Ask first, and record it in `crontab.txt` if it
happens.
