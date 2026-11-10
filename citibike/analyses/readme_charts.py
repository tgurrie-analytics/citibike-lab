"""Generate the README charts from the prod marts.

Usage (from the repo root, with the venv active and .env filled in):
    pip install matplotlib pandas
    python analyses/readme_charts.py

Writes PNGs to docs/images/.
"""
import os
import pathlib

import matplotlib.pyplot as plt
import pandas as pd
from databricks import sql

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

SCHEMA = "workspace.citibike_prod"
OUT_DIR = pathlib.Path("docs/images")

SERIES = ["#2a78d6", "#eb6834"]  # validated categorical slots 1 and 2
INK = "#1f1f1e"
MUTED = "#6b6a63"
GRID = "#e4e3de"
SURFACE = "#fcfcfb"

TRIPS_BY_HOUR = f"""
    select
        start_hour_local as hour,
        rider_type,
        count(*) / count(distinct trip_date_local) as avg_trips
    from {SCHEMA}.fct_trips
    group by 1, 2
    order by 1, 2
"""

AVAILABILITY_BY_HOUR = f"""
    with snapshots as (
        select
            hour(from_utc_timestamp(pulled_at_utc, 'America/New_York')) as hour,
            num_bikes_available = 0 and is_renting as is_empty,
            num_docks_available = 0 and is_returning as is_full
        from {SCHEMA}.stg_station_status
        where is_installed
          and pulled_at_utc >= timestamp'2026-10-22 00:00:00'
    )
    select
        hour,
        avg(cast(is_empty as int)) as share_empty,
        avg(cast(is_full as int)) as share_full
    from snapshots
    group by 1
    order by 1
"""


def query(statement):
    with sql.connect(
        server_hostname=os.environ["DATABRICKS_SERVER_HOSTNAME"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(statement)
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
    return pd.DataFrame(rows, columns=cols)


def style(ax, title, subtitle, ylabel):
    ax.set_facecolor(SURFACE)
    ax.figure.set_facecolor(SURFACE)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="y", color=GRID, linewidth=1)
    ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED, length=0, labelsize=10)
    ax.set_xticks(range(0, 24, 3))
    ax.set_xticklabels([f"{h % 12 or 12}{'am' if h < 12 else 'pm'}" for h in range(0, 24, 3)])
    ax.set_xlim(-0.5, 25.5)
    ax.set_ylabel(ylabel, color=MUTED, fontsize=10)
    ax.text(0, 1.12, title, transform=ax.transAxes, fontsize=14, fontweight="bold", color=INK)
    ax.text(0, 1.05, subtitle, transform=ax.transAxes, fontsize=10, color=MUTED)


def plot_lines(df, series, labels, title, subtitle, ylabel, path, pct=False):
    fig, ax = plt.subplots(figsize=(9, 4.8), dpi=150)
    ends = []
    for col, label, color in zip(series, labels, SERIES):
        ax.plot(df["hour"], df[col], color=color, linewidth=2, label=label)
        ends.append([float(df.iloc[-1][col]), label])
    # nudge end labels apart so they never overlap
    gap = 0.06 * float(df[series].max().max())
    ends.sort()
    for i in range(1, len(ends)):
        if ends[i][0] - ends[i - 1][0] < gap:
            ends[i][0] = ends[i - 1][0] + gap
    for y, label in ends:
        ax.text(23.4, y, label, color=INK, fontsize=10, va="center")
    if pct:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:.0%}"))
    else:
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.set_ylim(bottom=0)
    style(ax, title, subtitle, ylabel)
    ax.legend(loc="upper left", frameon=False, fontsize=10, labelcolor=INK)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE)
    plt.close(fig)
    print(f"wrote {path}")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    trips = query(TRIPS_BY_HOUR)
    trips["avg_trips"] = trips["avg_trips"].astype(float)
    wide = trips.pivot(index="hour", columns="rider_type", values="avg_trips").reset_index()
    plot_lines(
        wide, ["member", "casual"], ["Member", "Casual"],
        "When members and casual riders ride",
        "Average trips per day by start hour, New York time (Feb–Mar 2026)",
        "Trips per day", OUT_DIR / "trips_by_hour.png",
    )

    avail = query(AVAILABILITY_BY_HOUR)
    for c in ("share_empty", "share_full"):
        avail[c] = avail[c].astype(float)
    plot_lines(
        avail, ["share_empty", "share_full"], ["Empty", "Full"],
        "When stations run out of bikes or docks",
        "Share of active stations with no bikes (empty) or no docks (full), by hour (from 22 Oct 2026)",
        "Share of stations", OUT_DIR / "station_availability.png", pct=True,
    )


if __name__ == "__main__":
    main()
