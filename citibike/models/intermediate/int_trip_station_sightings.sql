with sightings as (
    select
        start_station_id as station_short_name,
        start_station_name as station_name,
        start_lat as lat,
        start_lng as lng,
        started_at_utc as seen_at_utc
    from {{ ref('stg_trips') }}
    where start_station_id is not null

    union all

    select
        end_station_id,
        end_station_name,
        end_lat,
        end_lng,
        ended_at_utc
    from {{ ref('stg_trips') }}
    where end_station_id is not null
)

select
    station_short_name,
    max_by(station_name, seen_at_utc) as latest_name_in_trips,
    avg(lat) as avg_lat,
    avg(lng) as avg_lng,
    min(seen_at_utc) as first_seen_utc,
    max(seen_at_utc) as last_seen_utc,
    count(*) as trip_appearances
from sightings
group by station_short_name