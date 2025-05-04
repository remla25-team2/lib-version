import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.lib_version.version_util import VersionUtil

# Make sure the directory exists
os.makedirs("src/lib_version", exist_ok=True)
with open("src/lib_version/version.json", "w") as f:
    json.dump({"version": VersionUtil.get_version()}, f)