import argparse
import datetime
import gzip
import json
import pathlib

import requests

FEEDS = {
    "station_status": "https://gbfs.lyft.com/gbfs/1.1/bkn/en/station_status.json",
    "station_information": "https://gbfs.lyft.com/gbfs/1.1/bkn/en/station_information.json",
}


def capture(name, url, pulled_at):
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    out_dir = pathlib.Path("data/landing") / f"feed={name}" / f"date={pulled_at:%Y-%m-%d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{name}_{pulled_at:%Y%m%dT%H%M%SZ}.json.gz"
    record = {"pulled_at": pulled_at.isoformat(), "source_url": url, "payload": payload}
    with gzip.open(out_file, "wt", encoding="utf-8") as f:
        json.dump(record, f)
    n = len(payload["data"]["stations"])
    print(f"{name}: {n} stations -> {out_file} ({out_file.stat().st_size / 1024:.0f} KB)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--feeds", nargs="+", default=list(FEEDS), choices=list(FEEDS))
    args = parser.parse_args()
    pulled_at = datetime.datetime.now(datetime.timezone.utc)
    for name in args.feeds:
        capture(name, FEEDS[name], pulled_at)


if __name__ == "__main__":
    main()