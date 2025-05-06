import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from .version_util import VersionUtil
import re

class PackageBuilder:
    def __init__(self, package_dir=".", output_dir=None, version_override=None):
        """
        Initialize package builder
        
        Args:
            package_dir: Directory containing the package to build
            output_dir: Directory to store build artifacts (default: {package_dir}/dist)
            version_override: Override the version instead of using git tags
        """
        self.package_dir = os.path.abspath(package_dir)
        self.output_dir = output_dir or os.path.join(self.package_dir, "dist")
        self.version_override = version_override
        
    def _parse_version(self, version_str):
        """Parse semantic version string into components."""
        pattern = r"^v?(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.-]+))?$"
        match = re.match(pattern, version_str)
        if match:
            major, minor, patch = map(int, match.groups()[:3])
            prerelease = match.group(4)
            return (major, minor, patch, prerelease)
        return None
        
    def _format_version(self, major, minor, patch, prerelease=None):
        """Format version components into a version string."""
        version = f"{major}.{minor}.{patch}"
        if prerelease:
            version += f"-{prerelease}"
        return version

    def get_auto_version(self):
        """
        Get version with automatic patch bumping or pre-release suffix
        """
        try:
            # Get the current version from VersionUtil
            current_version = VersionUtil.get_version()
            version_parts = self._parse_version(current_version)
            if not version_parts:
                raise ValueError(f"Invalid version format: {current_version}")
            
            major, minor, patch, prerelease = version_parts
            
            # Check if we're on a tag
            is_on_tag = VersionUtil.is_on_tag()
            
            # If we're not on a tag, modify the version
            if not is_on_tag:
                branch = VersionUtil.get_branch()
                
                if branch in ["main", "master"]:
                    # On main branch, create a pre-release version
                    commits = VersionUtil.get_commit_count_since_tag()
                    prerelease = f"pre{commits}"
                    return self._format_version(major, minor, patch, prerelease)
                else:
                    # On other branches, bump patch version
                    return self._format_version(major, minor, patch + 1)
            
            # Return the current version if on a tag
            return current_version
            
        except Exception as e:
            print(f"Error getting auto version: {e}")
            return VersionUtil.get_version()

    def write_version_files(self, version):
        """
        Write version information to files
        """
        # Create src directory if it doesn't exist
        package_name = os.path.basename(self.package_dir.rstrip("/"))
        src_dir = os.path.join(self.package_dir, "src", package_name)
        os.makedirs(src_dir, exist_ok=True)
        
        # Write version to _version.py
        with open(os.path.join(src_dir, "_version.py"), "w") as f:
            f.write(f'__version__ = "{version}"\n')
        
        # Write metadata to version.json
        metadata = {
            "version": version,
            "commit": VersionUtil.get_commit_hash(),
            "branch": VersionUtil.get_branch(),
            "timestamp": subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S"]).decode().strip()
        }
        
        with open(os.path.join(src_dir, "version.json"), "w") as f:
            json.dump(metadata, f, indent=2)
            
        print(f"Version files written with version: {version}")
        return version
        
    def build(self, auto_bump=True, clean=True):
        """
        Build package with automatic version handling
        
        Args:
            auto_bump: If True, automatically bump version for non-tagged commits
            clean: If True, clean the output directory before building
        """
        try:
            # Determine version
            if self.version_override:
                version = self.version_override
            elif auto_bump:
                version = self.get_auto_version()
            else:
                version = VersionUtil.get_version()
                
            # Write version files
            self.write_version_files(version)
            
            # Create output directory if it doesn't exist
            os.makedirs(self.output_dir, exist_ok=True)
            
            # Clean output directory if requested
            if clean and os.path.exists(self.output_dir):
                for item in os.listdir(self.output_dir):
                    item_path = os.path.join(self.output_dir, item)
                    if os.path.isfile(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
            
            # Build the package using build
            cmd = [
                sys.executable, "-m", "build",
                "--outdir", self.output_dir,
                self.package_dir
            ]
            
            print(f"Building package with command: {' '.join(cmd)}")
            subprocess.check_call(cmd)
            
            print(f"Package built successfully with version {version}")
            return version, self.output_dir
        
        except Exception as e:
            print(f"Error building package: {e}")
            raise