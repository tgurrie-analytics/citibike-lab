import argparse
import pathlib

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv


def main():
    parser = argparse.ArgumentParser(description="Upload local files to a Databricks volume, keeping folder structure.")
    parser.add_argument("--local", required=True, help="Local folder to upload from")
    parser.add_argument("--volume", required=True, help="Volume folder to upload to")
    parser.add_argument("--pattern", default="*", help="Which files to include, e.g. '*.parquet'")
    args = parser.parse_args()

    load_dotenv()
    w = WorkspaceClient()

    local_root = pathlib.Path(args.local)
    files = sorted(p for p in local_root.rglob(args.pattern) if p.is_file())
    for local_file in files:
        relative = local_file.relative_to(local_root).as_posix()
        target = f"{args.volume.rstrip('/')}/{relative}"
        with open(local_file, "rb") as f:
            w.files.upload(target, f, overwrite=True)
        print(f"uploaded {local_file} -> {target}")

    print(f"{len(files)} files uploaded")


if __name__ == "__main__":
    main()