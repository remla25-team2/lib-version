import json
import os

__version__ = "0.0.0"
# Attempt to load version from version.json
with open(os.path.join(os.path.dirname(__file__), "version.json")) as f:
        __version__ = json.load(f)["version"]


from .version_util import VersionUtil
from .builder import PackageBuilder

__all__ = ["VersionUtil", "PackageBuilder"]