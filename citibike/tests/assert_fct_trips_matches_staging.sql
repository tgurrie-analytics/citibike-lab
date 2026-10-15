with staging as (
    select count(*) as n from {{ ref('stg_trips') }}
),
fact as (
    select count(*) as n from {{ ref('fct_trips') }}
)
select staging.n as staging_rows, fact.n as fact_rows
from staging cross join fact
where staging.n != fact.n