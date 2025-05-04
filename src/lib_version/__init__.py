import os
import json

# Try to get version from version.json
try:
    with open(os.path.join(os.path.dirname(__file__), "version.json")) as f:
        __version__ = json.load(f)["version"]
except (FileNotFoundError, KeyError):
    __version__ = "0.0.0"