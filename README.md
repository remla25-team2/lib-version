# lib-version
`lib-version` is a Python library and utility for managing and retrieving version information from Git repositories. It's designed to simplify versioning for Python projects by leveraging Git tags and providing automatic version management.

## Features
- Automate semantic versioning with Git tag integration
- Support for vX.Y tags with automatic patch versioning
- Development versions for untagged commits
- CLI tool for version management operations
- Seamless integration with GitHub Actions for automated releases
- Generate version files for your Python packages
- Auto-create tags with appropriate version increments

## Installation
```bash
pip install lib-version
```

Or from source:

```bash
git clone https://github.com/yourusername/lib-version.git
cd lib-version
pip install -e .
```

## Usage

### Library Usage

You can access version information programmatically using the [VersionUtil](http://_vscodecontentref_/0) class:

```python
from lib_version.version_util import VersionUtil, VersionPart

# Get the latest version (Git tag or commit hash)
version = VersionUtil.get_version()
print(f"Version: {version}")

# Get additional metadata
metadata = VersionUtil.get_metadata()
print(f"Metadata: {metadata}")

# Parse a version string
parsed = VersionUtil.parse_version("v1.2.3")
print(f"Parsed version: {parsed}")
# (1, 2, 3, None)

# Bump a version
next_version = VersionUtil.bump_version("1.2.3", VersionPart.MINOR)
print(f"Next version: {next_version}")
# "1.3.0"
```

### CLI Usage

The `lib-version` command line tool provides a simple interface to manage your project's versioning:

#### Building Packages with Automatic Versioning

```bash
# Basic usage - will determine version automatically and build the package
lib-version

# Specify package directory
lib-version --package-dir ./my_package

# Override version
lib-version --version 1.2.3
```

#### Version Information

```bash
# Get the current version
lib-version --get-version

# Show version metadata
lib-version --info

# Get the next development version
lib-version --get-dev-version
```

#### Version Management

```bash
# Bump the version and create a tag
lib-version --bump patch
lib-version --bump minor
lib-version --bump major

# Create a new tag and push it
lib-version --create-tag v1.2.3 --push

# Get the next patch version for a specific major.minor
lib-version --get-next-patch-version 1 2
```

## Workflow Examples

### Basic Workflow

1. Development starts with a `v1.0` tag
2. For releases:
```bash
# Create a new release with the next minor version
lib-version --bump minor --push
# Build the package with the new version
lib-version
```
3. For pre-releases from main:
```bash
# Just build - it will create a development version
lib-version
```

### Version Tag Format

The library supports two tag formats:

1. `vX.Y` (e.g., `v1.0`): When building with this tag, it will automatically find the next patch version
2. `vX.Y.Z` (e.g., `v1.0.0`): Explicit version, used as-is

### GitHub Actions Integration

The included workflow automatically:

1. For tagged commits (`v*.*` or `v*.*.*`): Builds and publishes a release
2. For commits to [main](http://_vscodecontentref_/1): Builds with a development version and creates a pre-release
3. For pull requests: Runs tests only

## How It Works

- When you build with a `vX.Y` tag (like `v1.2`), it looks for existing `v1.2.*` tags, finds the highest patch number, and creates the next one (e.g., `v1.2.3`)
- When building untagged commits, it generates a PEP 440 compliant development version like `1.2.3.dev12+main.a1b2c3d`