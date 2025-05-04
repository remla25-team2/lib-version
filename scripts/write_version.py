import json
from lib_version.version_util import VersionUtil

with open("lib_version/version.json", "w") as f:
    json.dump({"version": VersionUtil.get_version()}, f)
