import argparse
import datetime
import glob
import pathlib

import pyarrow as pa
import pyarrow.csv as pacsv
import pyarrow.parquet as pq

TEXT_COLUMNS = [
    "ride_id", "rideable_type", "started_at", "ended_at",
    "start_station_name", "start_station_id",
    "end_station_name", "end_station_id", "member_casual",
]


def main():
    parser = argparse.ArgumentParser(description="Convert one month of Citi Bike trip CSVs to Parquet.")
    parser.add_argument("month", help="Month to convert, as YYYYMM, e.g. 202603")
    args = parser.parse_args()

    csv_files = sorted(glob.glob(f"data/trips/{args.month}-citibike-tripdata_*.csv"))
    if not csv_files:
        raise SystemExit(f"No CSV files found for month {args.month}")

    convert_options = pacsv.ConvertOptions(column_types={c: pa.string() for c in TEXT_COLUMNS})
    out_dir = pathlib.Path("data/parquet/trips") / f"month={args.month}"
    out_dir.mkdir(parents=True, exist_ok=True)
    loaded_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    total = 0
    for f in csv_files:
        table = pacsv.read_csv(f, convert_options=convert_options)
        n = table.num_rows
        table = table.append_column("source_file", pa.array([pathlib.Path(f).name] * n))
        table = table.append_column("loaded_at", pa.array([loaded_at] * n))
        out_file = out_dir / (pathlib.Path(f).stem + ".parquet")
        pq.write_table(table, out_file, compression="zstd")
        total += n
        print(f"{f}: {n:,} rows -> {out_file} ({out_file.stat().st_size / 1e6:.1f} MB)")

    print(f"Total rows written: {total:,}")


if __name__ == "__main__":
    main()