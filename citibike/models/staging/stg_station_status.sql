with snapshots as (
    select * from {{ source('citibike_raw', 'station_status_snapshots') }}
)

select
    cast(s.pulled_at as timestamp) as pulled_at_utc,
    st.station_id,
    st.legacy_id,
    st.num_bikes_available,
    st.num_ebikes_available,
    st.num_bikes_disabled,
    st.num_docks_available,
    st.num_docks_disabled,
    st.num_scooters_available,
    cast(st.is_installed as boolean) as is_installed,
    cast(st.is_renting as boolean) as is_renting,
    cast(st.is_returning as boolean) as is_returning,
    case
        when st.last_reported > 86400 then timestamp_seconds(st.last_reported)
    end as last_reported_utc
from snapshots s
lateral view explode(s.payload.data.stations) as st