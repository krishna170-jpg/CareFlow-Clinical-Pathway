
{{ config(materialized='table') }}

SELECT
    case_id,
    COUNT(*) AS event_count,
    MIN(event_timestamp) AS case_start_time,
    MAX(event_timestamp) AS case_end_time,
    TIMESTAMP_DIFF(
        MAX(event_timestamp),
        MIN(event_timestamp),
        MINUTE
    ) AS case_duration_minutes,
    ARRAY_AGG(
        activity IGNORE NULLS
        ORDER BY event_timestamp, sequence
        LIMIT 1
    )[SAFE_OFFSET(0)] AS first_activity,
    ARRAY_AGG(
        activity IGNORE NULLS
        ORDER BY event_timestamp DESC, sequence DESC
        LIMIT 1
    )[SAFE_OFFSET(0)] AS last_activity,
    MAX(age) AS age,
    MAX(gender) AS gender,
    MAX(triage_code) AS triage_code,
    MAX(disposition_desc) AS disposition_desc
FROM {{ ref('stg_careflow_events') }}
WHERE case_id IS NOT NULL
GROUP BY case_id
