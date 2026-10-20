CareFlow — Clinical Pathway Analytics

Overview

CareFlow is a healthcare analytics project designed to analyze clinical event logs, understand patient journeys, and identify patterns in clinical pathways.

Technologies Used

- Google BigQuery — data storage and SQL analytics
- dbt — data cleaning, transformation, and data modeling
- Looker Studio — interactive analytics dashboard
- GitHub — project version control and documentation

Data Pipeline

1. Raw clinical event logs are stored in BigQuery.
2. dbt transforms raw events into staging models.
3. Case-level metrics are calculated, including event counts and case duration.
4. Clinical activity transitions are aggregated to analyze patient pathways.
5. Looker Studio visualizes key metrics and pathway patterns.

Key Analytics

- Total cases and total events
- Average and longest case duration
- Most frequent clinical activities
- Transitions between clinical activities

Project Structure

- "models/stg_careflow_events.sql" — staging model
- "models/fct_careflow_cases.sql" — case-level metrics
- "models/fct_careflow_pathways.sql" — clinical pathway transitions
- "models/schema.yml" — data quality tests

Dashboard

Live Dashboard

"Open CareFlow Clinical Pathway Analytics" (https://datastudio.google.com/reporting/548e1c3e-fbfb-4992-bd7f-db9c6ecef44a)

Data Privacy

This repository should contain SQL models and documentation only. Do not commit patient-level data, credentials, access tokens, or private configuration files.

Purpose

This project demonstrates skills in SQL analytics, data transformation, process mining concepts, data quality testing, and dashboard development.# CareFlow-Clinical-Pathway
Dataset Engineering & Validation

The CareFlow event-log dataset was reviewed for data quality, consistency, and process-mining readiness.

Validation artifacts

Validation Report: CareFlow_Validation_Report.docx

Data Dictionary and Validation Results: CareFlow_Validation_and_Data_Dictionary.xlsx

The review covers event-log structure, missing values, duplicate records, timestamp consistency, sequence continuity, and activity summaries.

Important: The validation findings apply to the reviewed CSV file. They do not independently verify the BigQuery table or establish clinical correctness. Review potentially sensitive data before sharing files publicly.
