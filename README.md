# lib-version

`lib-version` is a Python library and utility for managing and retrieving version information from Git repositories. It is designed to simplify versioning for Python projects by leveraging Git tags and commit metadata.

## Features

- Retrieve the latest Git tag as the version.
- Fallback to the current commit hash if no tags are available.
- Retrieve additional metadata such as the current branch and commit hash.
- Automatically write version metadata to a JSON file during the build process.
- Seamless integration with GitHub Actions for automated releases.


# Usage
Accessing Version Information
You can access version information programmatically using the `VersionUtil` class:

```python
from lib_version.version_util import VersionUtil

# Get the latest version (Git tag or commit hash)
version = VersionUtil.get_version()
print(f"Version: {version}")

# Get additional metadata
metadata = VersionUtil.get_metadata()
print(f"Metadata: {metadata}")
```