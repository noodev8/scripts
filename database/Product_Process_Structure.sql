== Weekly 
== Run at any time and ok to run multiple times if needed. It will overide data for the week.

1. Clean sales Database
clean_sales.sql
Table: sales

2. Refresh Sales Data
refresh_performance.sql
Table: performance
Table: groupid_performance

3. Snapshot
weekly_snapshot.sql
Table: groupid_performance_week


--- Weekly meeting for progress update
--- Bi-Weekly meeting for clearance check

- Reason Code Options
Overstock
Low Sales
High Demand
Seasonal Change
Competitor Price
Promotion
Profit Opportunity
Manual Review

-- INSERT Price change
INSERT INTO price_change_log (
    groupid, channel, old_price, new_price, change_date, reason_code, changed_by, reason_notes
) VALUES (
    'YOUR_GROUPID', 'SHP', 49.99, 44.99, CURRENT_DATE, 'Overstock', 'Your Name',null
);


