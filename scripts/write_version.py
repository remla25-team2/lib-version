import json
import os
import subprocess
from lib_version.version_util import VersionUtil
# Get version
version = VersionUtil.get_version()

# Make sure the directory exists
os.makedirs("src/lib_version", exist_ok=True)

# Write metadata to version.json
metadata = {
    "version": version,
    "commit": subprocess.check_output(["git", "rev-parse", "--short", "HEAD"]).decode().strip(),
    "branch": subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode().strip()
}

with open("src/lib_version/version.json", "w") as f:
    json.dump(metadata, f, indent=2)
    print(f"Writing version info: {version}")