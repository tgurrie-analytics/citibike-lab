with source as (
    select * from {{ source('citibike_raw', 'trips') }}
),

typed as (
    select
        ride_id,
        rideable_type,
        member_casual as rider_type,
        to_timestamp(started_at) as started_at_local,
        to_timestamp(ended_at) as ended_at_local,
        start_station_id,
        start_station_name,
        end_station_id,
        end_station_name,
        start_lat,
        start_lng,
        end_lat,
        end_lng,
        source_file,
        loaded_at
    from source
)

select
    *,
    to_utc_timestamp(started_at_local, 'America/New_York') as started_at_utc,
    to_utc_timestamp(ended_at_local, 'America/New_York') as ended_at_utc,
    timestampdiff(
        SECOND,
        to_utc_timestamp(started_at_local, 'America/New_York'),
        to_utc_timestamp(ended_at_local, 'America/New_York')
    ) as duration_seconds,
    end_station_id is null as is_missing_end_station
from typed