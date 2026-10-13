{{ config(severity='warn') }}

select ride_id, started_at_local, ended_at_local, duration_seconds
from {{ ref('stg_trips') }}
where duration_seconds < 0