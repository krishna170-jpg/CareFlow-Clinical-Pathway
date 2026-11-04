# CareFlow — Daily Development Log

**Date:** 4 November 2026  
**Project:** CareFlow: Clinical Pathway Process Mining  
**Repository:** `krishna170-jpg/CareFlow-Clinical-Pathway`

## Current development focus

CareFlow is being developed as a clinical pathway and patient-flow analytics application. The priority is to improve operational visibility while preserving the existing Streamlit app, authentication, data connections, and deployed experience.

## Experimental feature work

### Patient Journey Sankey
An experimental version has been prepared to summarize observed transitions between recorded activities. It shows transition frequency and is not intended to prescribe a clinical pathway.

### Bottleneck Detection
An experimental version has been prepared to rank recorded activity transitions by observed waiting time. These intervals are not automatically confirmed clinical delays or length-of-stay measurements.

## Project components to preserve

- `app.py` — main Streamlit application.
- `careflow_core.py` — shared data and analytics helpers.
- `careflow_pm.py` — event-log preparation and process-mining helpers.
- `CareFlow_requirements.txt` — Python dependencies.
- Supabase email/password authentication and configured application secrets.
- Existing dashboard, navigation, filters, and analytics pages.

## Data integrity and privacy principles

1. Use the selected event-log source for reported analytics.
2. Do not invent hospital metrics, patient counts, clinical thresholds, or performance claims.
3. Clearly label synthetic or demonstration values.
4. Avoid displaying patient-identifiable information in charts, screenshots, or public documentation.
5. Never commit API keys, passwords, service-account credentials, private patient data, or local secret files.
6. Treat process-mining outputs as operational summaries requiring domain review before real clinical use.

## Verification required before release

The experimental feature files previously passed Python syntax compilation. This does not confirm runtime correctness. Before merging changes into production `app.py`:

- [ ] Run the candidate app locally with project dependencies.
- [ ] Verify sign-in, sign-out, and protected-page behavior.
- [ ] Verify dashboard, sidebar navigation, and existing filters.
- [ ] Test Patient Journey Sankey with the intended event-log data.
- [ ] Test Bottleneck Detection with valid and missing timestamps.
- [ ] Confirm empty-data and error states are handled clearly.
- [ ] Review labels and interpretation of displayed metrics.
- [ ] Back up the current production `app.py`.
- [ ] Merge only tested changes and check the Streamlit deployment.

## Suggested next development sequence

1. Complete local regression testing.
2. Validate Sankey transition counts against the source event log.
3. Validate waiting-time calculations and timestamp handling.
4. Improve pathway comparison using observed pathway variants.
5. Review governance, access logging, and role-based access controls.
6. Document deployment and rollback steps.

## Release status

**Experimental features are pending runtime verification.**

This log records the development direction and outstanding checks. It does not claim that experimental features have been deployed or clinically validated.

---
*CareFlow development documentation — 4 November 2026.*
