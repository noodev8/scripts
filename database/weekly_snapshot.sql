WITH this_week AS (
    SELECT
        TO_CHAR(CURRENT_DATE, 'IYYY-"W"IW') AS year_week,
        CURRENT_DATE AS snapshot_date
),
source AS (
    SELECT
        this_week.year_week,
        this_week.snapshot_date,
        gp.*
    FROM groupid_performance gp, this_week
),
to_insert AS (
    SELECT s.*
    FROM source s
    LEFT JOIN groupid_performance_week existing
      ON existing.year_week = s.year_week
     AND existing.groupid = s.groupid
     AND existing.channel = s.channel
    WHERE existing.year_week IS NULL
)
INSERT INTO groupid_performance_week (
    year_week,
    snapshot_date,
    groupid,
    channel,
    brand,
    annual_profit,
    sold_qty,
    avg_profit_per_unit,
    avg_gross_margin,
    segment,
    notes,
    owner
)
SELECT
    year_week,
    snapshot_date,
    groupid,
    channel,
    brand,
    annual_profit,
    sold_qty,
    avg_profit_per_unit,
    avg_gross_margin,
    segment,
    notes,
    owner
FROM to_insert;
