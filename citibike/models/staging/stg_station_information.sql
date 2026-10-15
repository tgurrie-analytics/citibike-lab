with snapshots as (
    select * from {{ source('citibike_raw', 'station_information_snapshots') }}
)

select
    cast(s.pulled_at as timestamp) as pulled_at_utc,
    st.station_id,
    st.short_name,
    st.name as station_name,
    st.lat,
    st.lon as lng,
    st.capacity,
    st.region_id,
    st.station_type,
    st.has_kiosk
from snapshots s
lateral view explode(s.payload.data.stations) as st