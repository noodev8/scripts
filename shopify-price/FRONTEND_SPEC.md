# Brookfield Comfort — Internal Platform (Build Spec)

**Read this whole document first. It is self-contained — you (the building AI) have no other
context, no access to the owner's other repos, and no access to the pricing strategy docs.
Everything you need is here.**

> ## ⛔ Before you write any code
> This spec describes an architecture and a domain process. **Do not start building yet.**
> First: read it all, then **propose your implementation plan back to the owner and get explicit
> sign-off on the architecture and the §1 assumptions.** Only build once the owner agrees. If
> anything here is ambiguous or seems wrong for their setup, ask — don't guess.

---

## 0. What we're building

An **internal web tool for Brookfield Comfort** (a UK footwear e-commerce business — Birkenstock
and other brands, sold on Shopify and Amazon). It is a **modular platform**: a login, then a
dashboard of modules. We build **one module now — "Shopify Pricing" — and add others later**
(inventory, orders, analytics, etc.). So architect for multiple modules, but only implement
Shopify Pricing in v1. The dashboard should show "Shopify Pricing" as the first (only live) menu
tile, with room for future tiles.

The Shopify Pricing module lets a user set Shopify prices using an established process
(**segment → shortlist → drill-down → set price**), or by finding a product directly. The full
process and its reasoning are embedded in §5 — treat that as the source of truth for behaviour.

---

## 1. Assumptions — confirm with the owner before building

1. **Writes go to the database only.** The tool updates the existing Postgres DB and sets a
   `shopifychange = 1` flag. An **existing external nightly job pushes changed prices to Shopify** —
   this tool does **not** call the Shopify API.
2. **Auth = app accounts + JWT.** A small `app_users` table (username + bcrypt hash + display
   name). The logged-in user's display name is stored as `changed_by` on every change. Default
   seed user name: **`Andreas`**.
3. **Internal tool**, Shopify (`SHP`) channel only for v1, one price per style.
4. **Modular platform** — pricing is module 1; the shell (auth, dashboard, nav) is reusable.

---

## 2. Architecture (match the owner's existing projects)

The owner runs other apps (`lmslocal`, `meetwithfriends`) with a consistent shape. **Mirror it.**

**Two apps in one repo:**

```
brookfield-app/
  brookfield-server/     # Express API — owns the DB connection and all SQL. Runs on a VPS.
  brookfield-web/        # Next.js front end — calls the API over HTTP. Deploys to Vercel.
  docs/                  # deploy.txt, this spec, etc.
```

**Data flow:** `brookfield-web` (browser/Vercel) → HTTP (axios) → `brookfield-server` (Express,
VPS) → PostgreSQL. **The web app never connects to the database directly** — only the server does.

### brookfield-server (Express)
- **Stack:** Node + Express 4, `pg` (node-postgres) with a pool, `jsonwebtoken` (JWT auth),
  `bcrypt` (password hashing), `cors`, `helmet`, `express-rate-limit`, `dotenv`.
- **`database.js`** — a single `pg` Pool built from `DB_*` env vars, exporting a
  `query(text, params)` helper (parameterised queries only). Pattern:
  ```js
  const { Pool } = require('pg');
  const pool = new Pool({
    host: process.env.DB_HOST, port: process.env.DB_PORT, database: process.env.DB_NAME,
    user: process.env.DB_USER, password: process.env.DB_PASSWORD,
    max: 20, idleTimeoutMillis: 30000, connectionTimeoutMillis: 2000,
  });
  async function query(text, params = []) {
    const client = await pool.connect();
    try { return await client.query(text, params); } finally { client.release(); }
  }
  module.exports = { pool, query };
  ```
- **Routes = one file per endpoint** in `routes/`, kebab-case verb-noun (this is the owner's
  convention — e.g. `pricing-triage.js`, `pricing-apply.js`, `login.js`). `server.js` wires them.
- **`middleware/verifyToken.js`** — verifies the JWT `Authorization: Bearer` header, attaches
  `req.user` (`{ id, display_name }`). All pricing routes require it.
- Run with `node server.js` (dev: `nodemon`; prod: `pm2`).

### brookfield-web (Next.js)
- **Stack:** Next.js 15 (App Router, `src/app`), React 19, TypeScript, Tailwind CSS 3,
  `axios`, `react-hook-form`, `@heroicons/react`.
- **`src/lib/api.ts`** — a shared axios instance pointed at `process.env.NEXT_PUBLIC_API_URL`,
  attaching the stored JWT as `Authorization: Bearer <token>`.
- **`src/contexts/AuthContext.tsx`** — holds the logged-in user + token (persist token in
  `localStorage`/cookie), guards routes.
- **`src/app/`** route folders (see §7). **`src/components/`** shared UI. Tailwind for styling.
- Deploys to **Vercel**.

### API & client conventions (Brookfield house style)
**Follow the owner's `API-RULES.md` — it is authoritative and will be provided alongside this
spec.** The essentials (inlined so this doc stands alone):
- **Every API response is HTTP 200 with a `return_code` field** — `SUCCESS` or an error code
  (`MISSING_FIELDS`, `INVALID_*`, `NOT_FOUND`, `UNAUTHORIZED`, `FORBIDDEN`, `SERVER_ERROR`).
  **Never** use HTTP 4xx/5xx for API-level errors. Success payloads add data fields alongside
  `return_code`; errors add a `message`.
- **Every route file starts with a structured header block** (method, purpose, request payload,
  success response, return codes) and is heavily commented (explain *why*).
- **Add API logging to every route** (a small `utils/apiLogger.js`).
- **JWT carries only the user id.** Everything else (e.g. `display_name`) is looked up from the DB
  per request. Single `verifyToken` middleware; JWT config in `config/config.js`.
- **DB:** direct `pg`, central pool in `database.js` (`const { query } = require('../database')`),
  a `utils/transaction.js` `withTransaction` wrapper for atomic writes (use it for W1/W2), no N+1.
- **Frontend API client never throws on API-level errors** — it returns structured objects
  (`{ success, data? , error?, return_code? }`) and lets the calling component decide (toast,
  inline, redirect). Only genuine network failures throw.
- **No hard-coded secrets** — everything via `.env`; flag if a new var is needed.

### Folder layout to create
```
brookfield-server/
  server.js  database.js  .env  package.json
  middleware/ verifyToken.js
  routes/  login.js  pricing-segments.js  pricing-triage.js  pricing-drill.js
           pricing-find.js  pricing-apply.js  pricing-park.js
  scripts/ seed-user.js            # create the first app_users row
brookfield-web/
  src/app/  layout.tsx  page.tsx   # page.tsx -> redirect to /login or /dashboard
           login/page.tsx
           dashboard/page.tsx      # module menu (Shopify Pricing tile + future)
           pricing/page.tsx        # segment picker
           pricing/[segment]/page.tsx        # triage list
           pricing/style/[groupid]/page.tsx  # drill-down + set price
           pricing/find/page.tsx             # direct product search
  src/components/  PriceSetter.tsx  Timeline.tsx  ...
  src/contexts/AuthContext.tsx
  src/lib/api.ts
  .env  package.json  tailwind.config.js
docs/  deploy.txt  FRONTEND_SPEC.md
```

---

## 3. Environment files

Create these. **Fill secrets locally; never commit `.env`; never paste real DB creds into any
third-party tool.** The database is the same Postgres the owner's Python scripts already use —
copy the four `DB_*` values (and the DB password) from `C:\scripts\.env`.

### brookfield-server/.env
```
NODE_ENV=production
PORT=3020
CLIENT_URL=http://localhost:3000      # web origin(s) for CORS; set to the Vercel URL in prod

# PostgreSQL (Brookfield production DB) — copy these from C:\scripts\.env
DB_HOST=            # same as scripts/.env
DB_PORT=5432        # same as scripts/.env
DB_NAME=            # same as scripts/.env
DB_USER=            # same as scripts/.env
DB_PASSWORD=        # <-- fill from scripts/.env (do not commit)

# Auth
JWT_SECRET=         # <-- generate a long random string
JWT_EXPIRES_IN=12h
BCRYPT_ROUNDS=12
```

### brookfield-web/.env
```
NEXT_PUBLIC_API_URL=http://localhost:3020   # the brookfield-server base URL; set to VPS URL in prod
```

---

## 4. Database — tables the tool uses

The DB is a legacy schema. **These caveats are landmines — read them:**

- **`skusummary.shopifyprice`, `cost`, `minshopifyprice`, `maxshopifyprice` are stored as
  `character varying`, not numbers.** Read with `NULLIF(col,'')::numeric`. When **writing**
  `shopifyprice`, write a **string** formatted to 2 dp (e.g. `'36.95'`). Treat `rrp` and any
  price-ish column the same way.
- **Never use `skusummary.stockvariants` / `skusummary.variants`** — stale, can be a year old.
  Always derive stock from `localstock`.
- **Size = last 2 chars of the SKU code** (`RIGHT(code,2)`), EU size by design.
- **`skusummary.colour` is overloaded as a segmentation tag** (e.g. "Mocha" filed under "Brown"),
  so it's ambiguous. Use `title.shopifytitle` for a human-readable product name.
- Current sellable stock = `localstock` where `ordernum='#FREE' AND COALESCE(deleted,0)=0 AND qty>0`.

| Table | Columns used | Role |
|---|---|---|
| `skusummary` | `groupid`, `segment`, `shopifyprice`, `cost`, `rrp`, `minshopifyprice`, `maxshopifyprice`, `colour`, `width`, `season`, `shopifychange`, `next_shopify_price_review` (date) | Product master; the row updated on a price change |
| `sales` | `groupid`, `code`, `solddate` (date), `ordertime` (text `HH:MM`), `qty` (int), `soldprice` (numeric), `channel` | Demand history (`channel='SHP'`) |
| `localstock` | `groupid`, `code`, `ordernum`, `deleted`, `qty` | Current stock |
| `title` | `groupid`, `shopifytitle` | Human-readable product name |
| `price_change_log` | `groupid`, `channel`, `old_price`, `new_price`, `change_date` (default `CURRENT_DATE`), `reason_code`, `reason_notes`, `changed_by` | Audit — one row per change |
| `app_users` *(create this)* | `id serial pk`, `username text unique`, `password_hash text`, `display_name text`, `active bool default true` | App login + attribution |

`skusummary.next_shopify_price_review` (a `date`) is the **cooldown**: while it's a future date,
the style is hidden from the triage. Set it on every price change (see §5, §6).

---

## 5. Pricing module — domain & process (the source of truth for behaviour)

**Business context.** Brookfield sells mostly Birkenstock on Shopify (~95% of Shopify sales).
**Birkenstock cannot be re-ordered on demand** — it's ordered ~6 months ahead, so the stock in
hand is all there is; there's no "sold out → restock" lever (other brands can restock, but they're
a small minority here). The consequence: **the job is to squeeze maximum profit from the stock we
already hold.** A fast-selling style with thin stock is therefore a **price-up / harvest**
candidate (it'll sell through regardless, so a low price just donates margin) — not a restock flag.

The process is three stages, always **starting from a segment** (a category grouping in
`skusummary.segment`, e.g. `EVA-SEG`).

### Stage 1 — Triage (shortlist)
For a chosen segment, list the **top 10 in-stock styles by units sold in the last 30 days** on
Shopify. This is a sanity shortlist — "which styles are worth a look" — nothing more. Columns:
row number, units sold (30d), groupid, title, current stock. Rules: Shopify only; positive sales
only; **drop styles with 0 current stock** (nothing to price, and Birkenstock can't restock) and
top the list back up to 10; **drop "parked" styles** (a future `next_shopify_price_review`). Query
S2.

### Stage 2 — Drill-down (one style → decide)
For a picked style, show two blocks then a set-price control:
- **Header:** current price (`now`), `rrp`, `cost`, `stock`, and margin (`now − cost`, and %).
- **Pricing timeline:** one row per distinct price the style has sold at, **oldest first**, with
  the selling period, **units** sold at that price (`sold`), and the **pace** (`/wk`). The whole
  pricing decision is one relationship: *the price we charged vs how fast it sold, over time.*
  - **Why pace matters:** total units alone misleads across periods of different length — 25 sold
    over 4 weeks vs 17 over 2 weeks looks like more but is the same ~7/wk. Pace makes eras
    comparable. Show **both** units and pace.
  - **Pace maths (app-side):** `per_wk = units / weeks`, where `weeks = max(span_days, 7) / 7` and
    `span_days = last_sale_date − first_sale_date` for that price. The floor at 1 week stops a
    tiny era / single sale showing a wild number. Pace off a couple of sales is directional only.
  - **Honest caveat for the reader:** for seasonal Birkenstock, units rising as price rose can be
    *the season arriving, not the price working*. The cleaner signal is a price step where the
    pace **held** (a rise with no slowdown) — that's the evidence for going higher.
- **Size curve** (collapsible, default hidden): remaining stock by size. Size does **not** set the
  price — it's a guardrail before a **cut** (so you don't misread a sold-out core, e.g. 38/39
  gone, as dead demand). For a raise it barely matters.

### Stage 3 — Set price + review
The user sets a new price and a **review period** (both together). See §7's price control. On save:
apply the price and stamp the cooldown (§6, W1). If they don't want to change the price but want to
stop it re-surfacing, they can set just the review period (W2).

**The review cooldown (`next_shopify_price_review`).** So the triage doesn't keep re-surfacing a
style just handled, every decision sets a next-review date; until it passes, the style is hidden
from Stage 1. **A price change requires a review period** (no silent default — the user picks it,
same moment as the price). Suggested defaults by move type: **raise-probe ~7 days, cut-to-clear
~14, hold/healthy ~30** — suggest, let the user change.

**Attribution / notes.** `changed_by` = the logged-in user's display name. `reason_code` is left
**NULL** and `reason_notes` blank — we deliberately don't capture a reason in this tool.

---

## 6. Write rules (must be exact)

Wrap each in a **transaction**. `changed_by` = `req.user.display_name`.

### W1 — apply a price change (review period REQUIRED)
Reject if `reviewDays` missing or `< 1`. Enforce bounds server-side: block `< cost` or
`< minshopifyprice`; allow-but-flag `> maxshopifyprice` or `> rrp`.
```sql
-- shopifyprice is varchar: pass new price as a 2dp STRING (e.g. '36.95').
UPDATE skusummary
   SET shopifyprice = $2,
       shopifychange = 1,
       next_shopify_price_review = CURRENT_DATE + $3::int   -- reviewDays
 WHERE groupid = $1;

INSERT INTO price_change_log
   (groupid, channel, old_price, new_price, reason_code, reason_notes, changed_by)
VALUES ($1, 'SHP', $4, $5, NULL, '', $6);
-- $4 old price (numeric), $5 new price (numeric), $6 changed_by. change_date defaults to today.
```
`shopifychange = 1` is what the nightly Shopify sync consumes — never skip it.

### W2 — park only ("no change, set review")
```sql
UPDATE skusummary
   SET next_shopify_price_review = CURRENT_DATE + $2::int
 WHERE groupid = $1;
```

---

## 7. Web — screens, flows, and the price control

- **/login** — username + password → `POST /login` → store JWT → go to /dashboard.
- **/dashboard** — the platform menu. A tile grid; **"Shopify Pricing"** is the one live tile
  (→ /pricing). Leave visible room / placeholders for future modules.
- **/pricing** — segment picker (list from `GET /pricing-segments`). Also a "Find a product"
  entry (→ /pricing/find).
- **/pricing/[segment]** — the numbered triage list (`GET /pricing-triage`). Row click →
  /pricing/style/[groupid].
- **/pricing/style/[groupid]** — drill-down (`GET /pricing-drill`): header, timeline (units + /wk),
  collapsible size curve, and the price control below.
- **/pricing/find** — search box (`GET /pricing-find?term=`) matching groupid or title → pick →
  drill page.

### The set-price control (reduced typing — a priority)
```
   Current: 36.95        Margin: 16.12 (44%)      RRP 50.00   min 35.99   max 45.00

   New price:   [ −£1 ] [ −50p ]   [   37.95   ]   [ +50p ] [ +£1 ] [ +£2 ]
                                        ^ big, editable; margin recalculates live

   Review in:   ( 3 ) ( 5 ) ( 7* ) ( 10 ) ( 14 ) ( 30 ) ( 90 )  days   ← required to Apply
                                    ^ single-select chips; pre-suggest per move type

   [ Apply price ]      [ No change — just set review ]      [ Cancel ]
```
- Nudge buttons (−£1/−50p/+50p/+£1/+£2) step the editable price field; margin updates live.
- Bounds: disable **Apply** if `< cost` or `< minshopifyprice`; show a warning (still allow) if
  `> max` or `> rrp`. **Enforce server-side too.**
- Review chips mirror the owner's desktop app (3/5/7/10/14/30/90). Required for a price change.
- "No change — just set review" needs only a chip → calls park (W2).
- On success: show new price + review date, return to the list (the style is now hidden from that
  segment's triage until the review date).

---

## 8. API endpoints (one route file each)

All except `login` require a valid JWT (`verifyToken`). `changed_by` = `req.user.display_name`,
resolved by `verifyToken` from the token's user id (§9) — never sent by the client. All responses
use the `return_code` envelope (§2 conventions / API-RULES.md).

| Route file | Method / path | Body/params | Does |
|---|---|---|---|
| `login.js` | `POST /login` | `{username, password}` | bcrypt-check vs `app_users`, return `{token, display_name}` |
| `pricing-segments.js` | `GET /pricing-segments` | — | S1 |
| `pricing-triage.js` | `GET /pricing-triage` | `segment`, `days?`, `limit?` | S2 |
| `pricing-drill.js` | `GET /pricing-drill` | `groupid`, `days?` | S3 + S4 (+ pace) + S5 |
| `pricing-find.js` | `GET /pricing-find` | `term` | S6 |
| `pricing-apply.js` | `POST /pricing-apply` | `{groupid, newPrice, reviewDays}` | W1 (+ bounds) |
| `pricing-park.js` | `POST /pricing-park` | `{groupid, reviewDays}` | W2 |

### SQL for the reads

**S1 — segments**
```sql
SELECT segment, COUNT(*) AS styles
FROM skusummary WHERE segment IS NOT NULL AND segment <> ''
GROUP BY segment ORDER BY segment;
```

**S2 — triage** — `$1` segment, `$2` days (30), `$3` limit (10)
```sql
WITH win AS (
  SELECT s.groupid,
         SUM(s.qty) AS units,
         MAX(s.solddate::text || ' ' || LPAD(COALESCE(s.ordertime,'00:00'),5,'0')) AS last_ts
  FROM sales s
  JOIN skusummary ss ON ss.groupid = s.groupid
  WHERE ss.segment = $1 AND s.channel='SHP'
    AND s.qty > 0 AND s.soldprice > 0
    AND s.solddate >= CURRENT_DATE - $2::int
    AND (ss.next_shopify_price_review IS NULL OR ss.next_shopify_price_review <= CURRENT_DATE)
  GROUP BY s.groupid
),
stk AS (
  SELECT groupid, SUM(qty) AS stock FROM localstock
  WHERE ordernum='#FREE' AND COALESCE(deleted,0)=0 AND qty>0
  GROUP BY groupid
)
SELECT w.groupid, w.units, st.stock, t.shopifytitle
FROM win w
JOIN stk st ON st.groupid = w.groupid            -- INNER JOIN drops 0-stock styles
LEFT JOIN title t ON t.groupid = w.groupid
ORDER BY w.units DESC, w.last_ts DESC
LIMIT $3::int;
```

**S3 — drill header** — `$1` groupid
```sql
SELECT
  NULLIF(ss.shopifyprice,'')::numeric    AS now,
  NULLIF(ss.cost,'')::numeric            AS cost,
  NULLIF(ss.rrp::text,'')::numeric       AS rrp,
  NULLIF(ss.minshopifyprice,'')::numeric AS minp,
  NULLIF(ss.maxshopifyprice,'')::numeric AS maxp,
  ss.colour, ss.width, ss.season, ss.next_shopify_price_review,
  t.shopifytitle,
  COALESCE((SELECT SUM(l.qty) FROM localstock l
            WHERE l.groupid=ss.groupid AND l.ordernum='#FREE'
              AND COALESCE(l.deleted,0)=0 AND l.qty>0),0) AS stock
FROM skusummary ss
LEFT JOIN title t ON t.groupid = ss.groupid
WHERE ss.groupid = $1;
```

**S4 — pricing timeline** — `$1` groupid, `$2` days (90). Compute pace app-side (§5).
```sql
SELECT soldprice, SUM(qty) AS units, MIN(solddate) AS first_at, MAX(solddate) AS last_at
FROM sales
WHERE groupid=$1 AND channel='SHP' AND qty>0 AND soldprice>0
  AND solddate >= CURRENT_DATE - $2::int
GROUP BY soldprice
ORDER BY MIN(solddate);
```
(Label a row's period end "now" when its `soldprice == now`. A just-changed price shows no row
until something sells at it.)

**S5 — size curve** — `$1` groupid
```sql
SELECT RIGHT(code,2) AS size, SUM(qty) AS qty FROM localstock
WHERE groupid=$1 AND ordernum='#FREE' AND COALESCE(deleted,0)=0 AND qty>0
GROUP BY RIGHT(code,2) ORDER BY size;
```

**S6 — find** — `$1` = `%term%`
```sql
SELECT ss.groupid, t.shopifytitle, ss.segment, NULLIF(ss.shopifyprice,'')::numeric AS now
FROM skusummary ss
LEFT JOIN title t ON t.groupid = ss.groupid
WHERE ss.groupid ILIKE $1 OR t.shopifytitle ILIKE $1
ORDER BY ss.groupid LIMIT 25;
```

---

## 9. Auth

- `app_users(id, username, password_hash, display_name, active)`. Seed one row via
  `scripts/seed-user.js` (bcrypt-hash a password): username of choice, `display_name = 'Andreas'`.
- `POST /login`: look up active user, `bcrypt.compare`, sign a JWT carrying **only `{ id }`** with
  `JWT_SECRET` / `JWT_EXPIRES_IN`, return `{ return_code: 'SUCCESS', token, display_name }`.
- `middleware/verifyToken.js`: read `Authorization: Bearer`, `jwt.verify`, then **look up the user
  by id** and attach `req.user = { id, display_name }` (per API-RULES: token holds id only, DB
  holds the rest). Apply to all pricing routes. So `changed_by` on a write = `req.user.display_name`
  resolved from the token's id — never sent by the client.
- Web stores the token (AuthContext) and axios attaches it. Redirect to /login when missing/expired.
- No public signup. Adding users = insert an `app_users` row (a small admin script is fine).

---

## 10. Guardrails

- All DB access is server-side, parameterised (no string interpolation).
- Validate every request body/params (e.g. with a small schema check): prices positive, 2 dp;
  `reviewDays` a positive integer.
- Enforce price bounds server-side (block `< cost` / `< min`; flag `> max` / `> rrp`).
- A price change with no `reviewDays` is rejected.
- Round money to 2 dp before writing; write `shopifyprice` as a string.
- CORS restricted to `CLIENT_URL`; `helmet`; rate-limit `login`.

---

## 11. Deployment (follow the owner's pattern)

**Server → VPS (PM2).** Add to `docs/deploy.txt`:
```
-- putty (brookfield)
cd /apps/brookfield/
git pull
rsync -av --delete --exclude='.env' --exclude='node_modules' --exclude='.git' --exclude='docs' \
  /apps/brookfield/brookfield-server/ /apps/production/brookfield-server/
cd /apps/production/brookfield-server
npm install
pm2 restart server.js --name brookfield_prod
```
The `.env` on the VPS holds the DB creds and `JWT_SECRET` (never rsynced/committed). Set
`CLIENT_URL` to the web origin and open the chosen `PORT`.

**Web → Vercel.**
```
cd brookfield-web
vercel --prod
```
Set `NEXT_PUBLIC_API_URL` in Vercel to the VPS server URL. (Since this is internal and hits a
production DB via the API, confirm with the owner whether the web should be public-behind-login on
Vercel or hosted internally — see §1.)

---

## 12. Out of scope for v1

- Talking to the Shopify API (the existing nightly job pushes prices).
- Amazon/FBA pricing; non-`SHP` channels; incoming/allocated stock; Google benchmark data.
- Bulk edits — v1 is one style at a time.
- Modules other than Shopify Pricing (but keep the shell modular for them).

## 13. Suggested build order

1. Scaffold both apps in the owner's structure; wire `database.js` + a `GET /health` that runs
   `SELECT NOW()`; confirm DB connectivity.
2. Auth: `app_users`, `seed-user.js`, `POST /login`, `verifyToken`, web AuthContext + /login.
3. Dashboard shell with the Shopify Pricing tile.
4. Pricing reads: segments → triage → drill (with pace) → find. Build the screens against real DB.
5. Pricing writes: apply (W1, bounds, required review) + park (W2), with the reduced-typing control.
6. Deploy per §11.

**Again: confirm the architecture and §1 assumptions with the owner before building.**
