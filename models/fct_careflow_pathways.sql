
{{ config(materialized='table') }}

WITH ordered_events AS (
    SELECT
        case_id,
        activity,
        event_timestamp,
        sequence,
        LEAD(activity) OVER (
            PARTITION BY case_id
            ORDER BY event_timestamp, sequence
        ) AS next_activity
    FROM {{ ref('stg_careflow_events') }}
    WHERE case_id IS NOT NULL
      AND activity IS NOT NULL
)

SELECT
    activity AS from_activity,
    next_activity AS to_activity,
    COUNT(*) AS transition_count,
    COUNT(DISTINCT case_id) AS cases_with_transition
FROM ordered_events
WHERE next_activity IS NOT NULL
GROUP BY from_activity, to_activity
ORDER BY transition_count DESC
