import os

from databricks import sql

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

VOLUME = "/Volumes/workspace/citibike_raw/landing"

COPY_STATEMENTS = {
    "trips": f"""
        COPY INTO workspace.citibike_raw.trips
        FROM '{VOLUME}/trips/'
        FILEFORMAT = PARQUET
        PATTERN = 'month=*/*.parquet'
        COPY_OPTIONS ('mergeSchema' = 'true')
    """,
    "station_status": f"""
        COPY INTO workspace.citibike_raw.station_status_snapshots
        FROM '{VOLUME}/gbfs/feed=station_status/'
        FILEFORMAT = JSON
        PATTERN = 'date=*/*.json.gz'
        FORMAT_OPTIONS ('multiLine' = 'true')
        COPY_OPTIONS ('mergeSchema' = 'true')
    """,
    "station_information": f"""
        COPY INTO workspace.citibike_raw.station_information_snapshots
        FROM '{VOLUME}/gbfs/feed=station_information/'
        FILEFORMAT = JSON
        PATTERN = 'date=*/*.json.gz'
        FORMAT_OPTIONS ('multiLine' = 'true')
        COPY_OPTIONS ('mergeSchema' = 'true')
    """,
}


def main():
    with sql.connect(
        server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    ) as conn:
        with conn.cursor() as cur:
            for name, statement in COPY_STATEMENTS.items():
                cur.execute(statement)
                rows = cur.fetchall()
                columns = [d[0] for d in cur.description]
                summary = dict(zip(columns, rows[0])) if rows else {}
                print(f"{name}: {summary}")


if __name__ == "__main__":
    main()