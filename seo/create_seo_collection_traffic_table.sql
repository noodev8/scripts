-- SEO: table to track Shopify collection SEO metadata + Search Console traffic over time.
-- One row per collection per snapshot_date, so we can trend clicks/impressions/position.

CREATE TABLE IF NOT EXISTS seo_collection_traffic (
    id               SERIAL PRIMARY KEY,
    snapshot_date    DATE NOT NULL,
    handle           TEXT NOT NULL,
    title            TEXT NOT NULL,
    products_count   INTEGER NOT NULL,
    url              TEXT NOT NULL,
    seo_title        TEXT,
    seo_description  TEXT,
    clicks           INTEGER NOT NULL DEFAULT 0,
    impressions      INTEGER NOT NULL DEFAULT 0,
    position         NUMERIC(5,1),
    created_at       TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (handle, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_seo_collection_traffic_handle ON seo_collection_traffic (handle);
CREATE INDEX IF NOT EXISTS idx_seo_collection_traffic_snapshot_date ON seo_collection_traffic (snapshot_date);
