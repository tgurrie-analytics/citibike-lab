with feed_latest as (
    select *
    from {{ ref('stg_station_information') }}
    qualify row_number() over (partition by short_name order by pulled_at_utc desc) = 1
),

trips as (
    select * from {{ ref('int_trip_station_sightings') }}
)

select
    coalesce(f.short_name, t.station_short_name) as station_short_name,
    f.station_id as feed_station_id,
    coalesce(f.station_name, t.latest_name_in_trips) as station_name,
    coalesce(f.lat, t.avg_lat) as lat,
    coalesce(f.lng, t.avg_lng) as lng,
    f.capacity,
    f.short_name is not null as is_in_current_feed,
    t.station_short_name is not null as has_trips,
    t.first_seen_utc,
    t.last_seen_utc,
    coalesce(t.trip_appearances, 0) as trip_appearances
from feed_latest f
full outer join trips t
    on f.short_name = t.station_short_name