import pathlib

from databricks.sdk import WorkspaceClient
from dotenv import load_dotenv

load_dotenv()

LOCAL_ROOT = pathlib.Path("data/landing")
VOLUME_ROOT = "/Volumes/workspace/citibike_raw/landing/gbfs"

w = WorkspaceClient()

files = sorted(LOCAL_ROOT.rglob("*.json.gz"))
for local_file in files:
    relative = local_file.relative_to(LOCAL_ROOT).as_posix()
    target = f"{VOLUME_ROOT}/{relative}"
    with open(local_file, "rb") as f:
        w.files.upload(target, f, overwrite=True)
    print(f"uploaded {local_file} -> {target}")

print(f"{len(files)} files uploaded")