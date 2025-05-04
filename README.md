# lib-version

`lib-version` is a Python library and utility for managing and retrieving version information from Git repositories. It is designed to simplify versioning for Python projects by leveraging Git tags and commit metadata.

## Features

- Retrieve the latest Git tag as the version.
- Fallback to the current commit hash if no tags are available.
- Retrieve additional metadata such as the current branch and commit hash.
- Automatically write version metadata to a JSON file during the build process.
- Seamless integration with GitHub Actions for automated releases.