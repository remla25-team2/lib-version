# lib-version
`lib-version` is a Python library and utility for managing and retrieving version information from Git repositories. It's designed to simplify versioning for Python projects by leveraging Git tags and providing automatic version management.

## Features
- Automate semantic versioning with Git tag integration
- Support for `vX.Y` tags with automatic patch versioning
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

You can access version information programmatically using the [`VersionUtil`](src/lib_version/version_util.py) class:

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

The `lib-version` command line tool provides a simple interface to manage your project's versioning. Run `lib-version --help` for all options.

#### Build Packages with Automatic Versioning

```bash
# Build the package in the current directory, auto-detect version from git
lib-version

# Specify a package directory
lib-version --package-dir ./my_package

# Specify output directory for build artifacts
lib-version --output-dir ./build_output

# Override the version (bypasses git tag detection)
lib-version --version 1.2.3

# Do not clean the output directory before building
lib-version --no-clean
```

#### Version Information

```bash
# Get the current version (from git tag or version file)
lib-version --get-version

# Show version metadata (version, commit, branch, timestamp)
lib-version --info

# Get the next development version (PEP 440 compliant)
lib-version --get-dev-version

# Get the next patch version for a given major.minor (e.g., v1.2)
lib-version --get-next-patch-version 1 2

# Get the next patch version based on the current version
lib-version --get-next-version
```

#### Version Management

```bash
# Bump the version and create a tag (does not push by default)
lib-version --bump patch
lib-version --bump minor
lib-version --bump major

# Create a new tag and optionally push it
lib-version --create-tag v1.2.3
lib-version --create-tag v1.2.3 --push

# Push tags created by bump or create-tag
lib-version --bump patch --push
```

### Using in a Workflow (GitHub Actions Example)

You can use `lib-version` in your CI/CD workflows to automate versioning and package publishing. For example, in a GitHub Actions workflow:

```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip
    pip install build lib-version

- name: Build package with automatic versioning
  run: |
    lib-version --package-dir . --output-dir dist

- name: Get package version
  id: get_version
  run: |
    VERSION=$(lib-version --get-version)
    echo "package_version=$VERSION" >> $GITHUB_OUTPUT
```

See [.github/workflows/release.yml](.github/workflows/release.yml) for a complete example.

### Using as a Dependency in Other Python Projects

Add `lib-version` to your `pyproject.toml` or `requirements.txt`:

**pyproject.toml**
```toml
[project.dependencies]
lib-version = "*"
```

**requirements.txt**
```
lib-version
```

Then, in your project code, you can use the library API:

```python
from lib_version.version_util import VersionUtil

__version__ = VersionUtil.get_version()
```

Or use the CLI in your build scripts or CI/CD pipelines.

## Workflow Examples

### Basic Workflow

1. Start development with a `v1.0` tag.
2. For releases:
    ```bash
    # Bump the minor version and push the new tag
    lib-version --bump minor --push
    # Build the package with the new version
    lib-version
    ```
3. For pre-releases from main:
    ```bash
    # Build with a development version
    lib-version
    ```

### Version Tag Format

- `vX.Y` (e.g., `v1.0`): When building with this tag, it will automatically find the next patch version.
- `vX.Y.Z` (e.g., `v1.0.0`): Explicit version, used as-is.

### GitHub Actions Integration

The included workflow automatically:

1. For tagged commits (`v*.*` or `v*.*.*`): Builds and publishes a release.
2. For commits to [`main`](https://github.com/yourusername/lib-version/tree/main): Builds with a development version and creates a pre-release.
3. For pull requests: Runs tests only.

## How It Works

- When you build with a `vX.Y` tag (like `v1.2`), it looks for existing `v1.2.*` tags, finds the highest patch number, and creates the next one (e.g., `v1.2.3`).
- When building untagged commits, it generates a PEP 440 compliant development version like `1.2.3.dev12+main.a1b2c3d`.

For more details, see the [source code](src/lib_version/) and [examples above](#usage).