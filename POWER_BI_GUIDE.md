# Power BI guide

1. Run `scripts/run_week3.py`.
2. In Power BI Desktop, choose **Get data → Text/CSV**.
3. Import `activity_counts.csv`, `pathway_frequencies.csv`, `transition_metrics.csv`, and `stage_metrics.csv` from the output directory.
4. Build visuals: event count by activity; top pathway frequencies by case count; transition pair by median/P90 elapsed minutes; stage-level event and case counts.
5. Refresh the CSV files after rerunning the script. Keep `cleaned_event_log.csv` and `case_summary.csv` private because they contain case-level data.

Power BI credentials/live connections are not configured by this package.
