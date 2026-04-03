1 - Download latest Google ads report from google into "downloads" folder
  - adcost_summary_30.csv
2 - Run python
python C:\scripts\google-ads\update_google_stock_track.py

3 - Check
SELECT * FROM google_stock_track ORDER BY snapshot_date DESC LIMIT 5;
