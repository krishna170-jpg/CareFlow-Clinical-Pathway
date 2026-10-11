
{{ config(materialized='view') }}

SELECT
    NULLIF(TRIM(CAST(case_id AS STRING)), '') AS case_id,
    NULLIF(TRIM(activity), '') AS activity,
    SAFE_CAST(timestamp AS TIMESTAMP) AS event_timestamp,
    SAFE_CAST(sequence AS INT64) AS sequence,
    SAFE_CAST(triage_code AS FLOAT64) AS triage_code,
    NULLIF(TRIM(initial_zone), '') AS initial_zone,
    SAFE_CAST(disposition_code AS INT64) AS disposition_code,
    NULLIF(TRIM(disposition_desc), '') AS disposition_desc,
    SAFE_CAST(age AS INT64) AS age,
    NULLIF(UPPER(TRIM(gender)), '') AS gender
FROM `careflow-analytics-511316.careflow_raw.raw_careflow_event_log`
