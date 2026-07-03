# Handoff prompt — Brookfield Comfort platform build

Paste this into a fresh AI session, and provide it two files alongside: `FRONTEND_SPEC.md`
(this folder) and `API-RULES.md` (the owner's house-style doc).

---

You're building an internal web platform for Brookfield Comfort, a UK footwear e-commerce
business. I'm giving you two documents — read BOTH completely before doing anything:

  1. FRONTEND_SPEC.md — the full build spec: architecture, the pricing domain/process,
     exact SQL, DB write rules, screens, env, and deployment.
  2. API-RULES.md — the house style for all API and client code. Authoritative for
     conventions (response envelope, error handling, route file headers, JWT, transactions).

Important framing and rules:
  - This is a Brookfield Comfort *platform*. We build ONE module now — "Shopify Pricing" —
    behind a login + dashboard shell that's ready for future modules. Don't build other modules.
  - DO NOT start coding yet. First read both docs, then propose your implementation plan
    (folder structure, stack, milestones) and confirm the "§1 Assumptions" with me. Only build
    after I sign off on the architecture.
  - Do NOT invent pricing logic. The process and the reasons for it are in spec §5 — mirror it
    exactly. The exact SQL (§8) and DB write rules (§6) are given; use them verbatim.
  - Heed the schema landmines the spec calls out (prices stored as varchar → cast on read /
    write as string; never use stockvariants; size = RIGHT(code,2); colour is a segmentation tag
    so use the title for display).
  - Follow API-RULES.md for all API/client conventions (HTTP 200 + return_code, route headers,
    JWT stores user id only, frontend client never throws on API errors, withTransaction).

Environment: Windows for dev. Deploy = server → VPS via PM2, web → Vercel (see spec §11).
The Postgres connection goes in .env (I'll fill it; the values match my existing scripts).

Start by reading both docs, then come back with your plan and any questions before writing code.
