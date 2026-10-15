{{
    config(
        materialized='incremental',
        incremental_strategy='merge',
        unique_key='ride_id',
        on_schema_change='append_new_columns'
    )
}}

with trips as (
    select * from {{ ref('stg_trips') }}
    {% if is_incremental() %}
    where cast(loaded_at as timestamp) > (select max(loaded_at_utc) from {{ this }})
    {% endif %}
)

select
    ride_id,
    start_station_id as start_station_short_name,
    end_station_id as end_station_short_name,
    rider_type,
    rideable_type,
    started_at_utc,
    ended_at_utc,
    started_at_local,
    ended_at_local,
    cast(started_at_local as date) as trip_date_local,
    hour(started_at_local) as start_hour_local,
    date_format(started_at_local, 'E') as start_day_of_week,
    dayofweek(started_at_local) in (1, 7) as is_weekend,
    duration_seconds,
    round(duration_seconds / 60.0, 2) as duration_minutes,
    {{ haversine_km('start_lat', 'start_lng', 'end_lat', 'end_lng') }} as straight_line_km,
    start_station_id = end_station_id as is_round_trip,
    is_missing_end_station,
    source_file,
    cast(loaded_at as timestamp) as loaded_at_utc
from trips