import glob
import gzip
import json
import pathlib

import pandas as pd

csv_files = sorted(
    f for f in glob.glob("data/trips/**/*.csv", recursive=True) if "__MACOSX" not in f
)
print("CSV files:", csv_files)

sample = pd.read_csv(csv_files[0], nrows=200_000, low_memory=False)
print("\nColumn types (from a 200k-row sample):")
print(sample.dtypes)
print("\nFirst 3 rows:")
print(sample.head(3).T)
print("\nShare of missing values per column (sample):")
print(sample.isna().mean().round(3))

ids = pd.concat(
    pd.read_csv(f, usecols=["start_station_id", "end_station_id"], dtype=str)
    for f in csv_files
)
print("\nTotal trips across all files:", len(ids))

info_file = sorted(
    pathlib.Path("data/landing/feed=station_information").rglob("*.json.gz")
)[-1]
with gzip.open(info_file, "rt") as f:
    stations = json.load(f)["payload"]["data"]["stations"]
short_names = {s["short_name"] for s in stations}
print("Stations in latest station_information snapshot:", len(short_names))

for col in ["start_station_id", "end_station_id"]:
    distinct_ids = set(ids[col].dropna())
    matched = distinct_ids & short_names
    share_of_trips = ids[col].isin(short_names).mean()
    print(
        f"{col}: {len(distinct_ids)} distinct IDs, {len(matched)} match short_name; "
        f"{share_of_trips:.1%} of trips match"
    )