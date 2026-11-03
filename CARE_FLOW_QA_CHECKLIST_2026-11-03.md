# CareFlow — Development QA Checklist

**Date:** 3 November 2026  
**Project:** CareFlow: Clinical Pathway Process Mining

This checklist records verification work to perform before promoting experimental analytics features into the deployed CareFlow application.

## Scope
- Patient Journey Sankey visualization
- Bottleneck Detection based on observed transition waiting times
- Existing application functionality that must remain stable

## 1. Local environment
- [ ] Back up the current working `app.py`.
- [ ] Keep the test app alongside `careflow_core.py` and `careflow_pm.py`.
- [ ] Confirm project dependencies are installed.
- [ ] Start the test app locally and check the terminal for errors.

## 2. Authentication and access
- [ ] Sign in using an approved test account.
- [ ] Confirm protected pages are not accessible while signed out.
- [ ] Confirm logout ends the session.
- [ ] Refresh after logout and verify the user remains signed out.
- [ ] Confirm existing role and access restrictions remain unchanged.

## 3. Existing application regression checks
- [ ] Dashboard opens successfully.
- [ ] Sidebar navigation opens every expected page.
- [ ] Existing filters update displayed results.
- [ ] Existing reports and charts render.
- [ ] Profile and account pages remain accessible to the correct user.
- [ ] No existing feature has been unintentionally removed.

## 4. Patient Journey Sankey
- [ ] Open Patient Flow and locate the Sankey visualization.
- [ ] Confirm it renders when valid transitions exist.
- [ ] Change the displayed transition limit and verify the chart updates.
- [ ] Check that link widths represent observed transition counts.
- [ ] Confirm patient identifiers are not exposed.
- [ ] Verify the empty-state message when there are too few events.
- [ ] Review activity labels and inferred stage colors.

## 5. Bottleneck Detection
- [ ] Open the Bottleneck Detection view.
- [ ] Confirm results use the selected event log.
- [ ] Check that average and median waiting times are labeled clearly.
- [ ] Change the ranking method and verify the ordering updates.
- [ ] Check how missing timestamps and negative intervals are handled.
- [ ] Verify the empty-state message when no valid transition times exist.
- [ ] Do not describe observed waiting time as a proven clinical delay.

## 6. Data integrity and safe interpretation
- [ ] Do not add invented hospital metrics or clinical thresholds.
- [ ] Label synthetic/demo values clearly.
- [ ] Do not expose patient-identifiable information in charts or logs.
- [ ] Do not call event-span duration “length of stay” unless supported by source data.
- [ ] Show errors without exposing secrets or credentials.

## 7. Release checklist
- [ ] Local testing is complete.
- [ ] Authentication and existing pages pass regression checks.
- [ ] Analytics outputs have been checked against the source event log.
- [ ] The current production `app.py` is backed up.
- [ ] Only the tested version is merged into `app.py`.
- [ ] Streamlit deployment is checked after the GitHub commit.

**Status:** Pending verification. Mark an item complete only after performing the test; syntax compilation alone is not enough.

---
*This is a software QA checklist, not clinical validation or certification for hospital use.*
