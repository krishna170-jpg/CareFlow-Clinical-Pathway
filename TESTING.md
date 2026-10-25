# CareFlow test plan

Tick each box. Write down anything that fails using the bug template at the bottom.

## 0. Before you start
- [ ] Run `python preflight.py` on your computer (or check the items by hand). It must say READY.
- [ ] Repo root has: `app.py`, `careflow_core.py`, `careflow_pm.py`, `requirements.txt`, `assets/` (3 SVG files).
- [ ] Streamlit Cloud > Settings > Secrets has `SUPABASE_URL`, `SUPABASE_KEY` (anon key), and optionally `ADMIN_EMAILS`, `SESSION_TIMEOUT_MIN`.
- [ ] `supabase_security.sql` has been run in Supabase, and your email is in `app_admins`.
- [ ] Reboot the app after the last upload. Test in a private/incognito window so you start signed out.
- [ ] Test data: your real event log, plus `test_kit/sample_event_log_SYNTHETIC.csv` (synthetic: 720 cases, 6 weeks, 5,108 events, columns `case_id, activity, timestamp, department, triage_level, arrival_mode`).

## 1. Sign-in and security
- [ ] Sign-in page loads with the lavender design, logo and no broken images; nothing loads from unsplash.com.
- [ ] Wrong password shows an error and does not sign in.
- [ ] Create account with a short password (under 8 characters) is rejected; mismatched passwords are rejected.
- [ ] Correct sign-in opens the dashboard. Log out returns to the sign-in page.
- [ ] **Two users at once:** sign in as user A in one browser and user B in a private window; each sees their own email in the sidebar and neither is logged out by the other.
- [ ] **Timeout:** set `SESSION_TIMEOUT_MIN = 1`, sign in, wait 2 minutes, click anything: you return to sign-in with the inactivity message. Set it back to 30.
- [ ] A non-admin cannot see the Access Log page; an admin (in `ADMIN_EMAILS` and `app_admins`) can, and it shows login and page-view rows.

## 2. Data loading and mapping
- [ ] Open **Data source**, upload the sample CSV. The dashboard shows 720 cases and 5,108 events.
- [ ] Open **Field mapping**: case ID, activity, timestamp and department are detected (fix by hand if not).
- [ ] Upload a file with no department column: the app creates demo labels and says so (chip and warning).
- [ ] Upload an empty file or a non-CSV: you get a clear message, not a crash.

## 3. Executive Dashboard
- [ ] Page title is fully visible (not hidden under the top toolbar).
- [ ] "What needs attention" lists cases, median time, last-7-days change, slowest stage and any data gaps.
- [ ] KPI tiles are equal height, numbers count up on load and end on the correct values.
- [ ] Patient flow cards appear in order; with no targets exactly one card shows "Potential bottleneck" in amber.
- [ ] Charts load and are readable; hover shows tooltips. Completeness bars grow.
- [ ] Export: all three download buttons have **visible white text**; the CSV and HTML files open and contain sensible numbers.

## 4. Filters
- [ ] Choose a department: counts change on every page, and a chip with a ✕ appears. Click the ✕: the filter clears.
- [ ] Narrow the dates; the chip appears; **Reset filters** clears everything.
- [ ] Choose filters that match nothing: you see a friendly "no data" message, not an error.
- [ ] Filters stay applied when you switch pages.

## 5. Stage Mapping & Targets
- [ ] Every activity is listed with an automatic stage ("Left ED" and "Ambulance Transfer" are Transfer / departure).
- [ ] Change "Triage" to Treatment: the dashboard flow updates (Assessment stage disappears or changes).
- [ ] Set Assessment target to 1 hour: that card turns **red** with "Over target" and a percentage; the amber label disappears; the summary box says "Over target".
- [ ] Set all targets back to 0: amber potential bottleneck returns.
- [ ] Download the JSON, **Reset to automatic mapping**, then load the JSON: your changes come back.
- [ ] Load a random non-JSON file: you get an error message, not a crash.

## 6. Predictive Model
- [ ] Arrival forecast expander shows a 7-day chart, a busiest hour and a back-test line (sample data has 6 weeks).
- [ ] Train with defaults (duration, random forest): results, feature importance chart, actual-vs-predicted chart appear.
- [ ] Change the seed and retrain: numbers change slightly; the same seed gives the same numbers.
- [ ] Switch to "Long case (yes/no)" and each algorithm in turn: each trains without error.
- [ ] Chronological split works. A threshold so high that no case is "long" gives a clear message.
- [ ] Try your own inputs and press Predict: only that section updates (the page does not reload fully).
- [ ] Both downloads (test predictions CSV, settings JSON) work.
- [ ] With fewer than 30 cases (strong filters) you see the "at least 30 cases" message.

## 7. Other pages (click each one once)
- [ ] Process Mining Explorer, Patient Flow, Clinical Pathways, Pathway Comparison, Process Discovery, Bed & Discharge, Task & Escalation, Care Coordination, Care Teams, Notifications, Reports, Data Quality, Data Dictionary, Insights, Security & Governance, Workspace pages.
- [ ] No red error boxes. Pages that need a missing column say what is needed instead of crashing.

## 8. Design and responsiveness
- [ ] Top navigation shows Analytics, Operations, Data & Governance, Workspace; the current page is highlighted. (Needs Streamlit 1.46+.)
- [ ] All buttons, tabs and pills have readable text. Grey text is readable on the lavender panel.
- [ ] Phone width (or browser at ~400px): panel margins shrink, tiles stack, flow cards scroll sideways, nothing is cut off.
- [ ] Browsers: latest Chrome, Safari, Firefox, Edge. Check one phone too.
- [ ] Turn on "Reduce motion" in your device settings: animations stop and everything is still readable.

## 9. Speed (with your real file)
- [ ] First load after upload: note the time. Changing a filter: should feel under ~3 seconds.
- [ ] Switching pages and back is faster the second time (cached).

## 10. Data checks (does it tell the truth?)
- [ ] Pick 3 cases by hand in the CSV and confirm their elapsed time on the Patient Flow page.
- [ ] Confirm the dashboard case and event counts equal `df.case_id.nunique()` and `len(df)`.
- [ ] Confirm one stage's average (for example Admission ≈ 0.33 hrs on the sample file).

## Known limits (not bugs)
- Departments are demo labels when the file has no department column.
- Stages are inferred from activity names until you map them.
- Mapping and targets last for the browser session; save the JSON to keep them.
- Google Fonts load from Google; if blocked, a fallback font is used.
- The model learns only from the file in view; it is not clinical guidance.

## Bug template
```
Page / step:
What I did:
What I expected:
What happened (paste the red error text or attach a screenshot):
Browser and device:
File used (real / sample):
```
