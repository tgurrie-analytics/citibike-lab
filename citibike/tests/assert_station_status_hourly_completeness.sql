{{ config(severity='error', warn_if='>0', error_if='>12') }}

with bounds as (
    select
        date_trunc('hour', min(pulled_at_utc)) as first_hour,
        date_trunc('hour', max(pulled_at_utc)) as last_hour
    from {{ ref('stg_station_status') }}
    where pulled_at_utc >= greatest((current_timestamp() - interval 7 days), cast('{{ var('station_status_reliable_from_utc') }}' as timestamp))
),

expected_hours as (
    select explode(sequence(first_hour, last_hour, interval 1 hour)) as hour_utc
    from bounds
),

captured_hours as (
    select distinct date_trunc('hour', pulled_at_utc) as hour_utc
    from {{ ref('stg_station_status') }}
)

select e.hour_utc as missing_hour_utc
from expected_hours e
left join captured_hours c on e.hour_utc = c.hour_utc
where c.hour_utc is null
order by missing_hour_utc