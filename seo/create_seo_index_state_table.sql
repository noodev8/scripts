-- SEO: track Google index state per collection over time.
--
-- Why this table exists (and why it stores no traffic columns):
-- clicks/impressions/position are retrievable from the GSC Search Analytics API
-- for 16 months at any granularity, so storing them duplicates a better source.
-- Index state is the opposite: the URL Inspection API is point-in-time only and
-- Google retains no history, so "when did this page get indexed?" is
-- unanswerable after the fact unless we snapshot it ourselves.
--
-- One row per collection per snapshot_date.

CREATE TABLE IF NOT EXISTS seo_index_state (
    id                  SERIAL PRIMARY KEY,
    snapshot_date       DATE NOT NULL,
    handle              TEXT NOT NULL,
    url                 TEXT NOT NULL,
    products_count      INTEGER,

    -- URL Inspection: indexStatusResult
    verdict             TEXT,        -- PASS / NEUTRAL / FAIL / VERDICT_UNSPECIFIED
    coverage_state      TEXT,        -- 'Submitted and indexed' / 'Crawled - currently not indexed' / 'URL is unknown to Google'
    indexing_state      TEXT,
    robots_txt_state    TEXT,
    page_fetch_state    TEXT,
    google_canonical    TEXT,
    user_canonical      TEXT,
    last_crawl_time     TIMESTAMPTZ,

    -- Orphan detection: no referring URLs = nothing internally links here.
    referring_urls      TEXT[],
    referring_url_count INTEGER,
    sitemaps            TEXT[],

    inspect_error       TEXT,        -- populated if the API call failed for this URL
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (handle, snapshot_date)
);

CREATE INDEX IF NOT EXISTS idx_seo_index_state_handle ON seo_index_state (handle);
CREATE INDEX IF NOT EXISTS idx_seo_index_state_snapshot_date ON seo_index_state (snapshot_date);
CREATE INDEX IF NOT EXISTS idx_seo_index_state_coverage ON seo_index_state (coverage_state);
