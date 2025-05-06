import os
import sys
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from .version_util import VersionUtil, VersionPart
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
        
    def determine_version(self):
        """
        Determine the version for the build based on various conditions.
        
        For vX.Y tags: Auto-determine next patch version
        For vX.Y.Z tags: Use as-is
        For untagged commits: Use dev versioning
        
        Returns:
            tuple: (version_string, is_new_tag)
        """
        # Override takes precedence
        if self.version_override:
            return self.version_override, False
        
        # Check if we're on a tagged commit
        if VersionUtil.is_on_tagged_commit():
            tag = VersionUtil.get_latest_tag()
            
            # Check if it's a vX.Y format (major.minor only)
            parsed = VersionUtil.parse_version(tag)
            print(f"Parsed version from tag: {parsed}")
            if parsed and parsed[2] is None:  # No patch specified
                # Get the next version for this major.minor
                version = VersionUtil.get_next_version_for_tag(tag)
                
                # Create and push the new version tag
                VersionUtil.create_tag(version, push=True)
                return version, True
            else:
                # It's a full version tag, use it directly (strip v prefix)
                version = tag[1:] if tag.startswith('v') else tag
                return version, False
        else:
            # For untagged commits, use dev versioning
            return VersionUtil.get_dev_version(), False
        
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
        metadata = VersionUtil.get_metadata()
        metadata["version"] = version
        
        with open(os.path.join(src_dir, "version.json"), "w") as f:
            json.dump(metadata, f, indent=2)

        # print where the version files are written
        print(f"Version files written to: {os.path.join(src_dir, '_version.py')}")
        print(f"Version files written to: {os.path.join(src_dir, 'version.json')}")
            
        print(f"Version files written with version: {version}")
        return version
        
    def build(self, create_tag=True, clean=True):
        """
        Build package with automatic version handling
        
        Args:
            create_tag: If True, create a new tag for vX.Y format tags
            clean: If True, clean the output directory before building
        """
        try:
            # Determine version and whether a new tag was created
            version, created_tag = self.determine_version()
            
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
            # Execute the build command with stdout and stderr
            result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode != 0:
                print(f"Build failed with error: {result.stderr.decode()}")
                raise Exception("Build failed")
            # Print the output of the build command
            print(result.stdout.decode())
            tag_info = " (new tag created)" if created_tag else ""
            print(f"Package built successfully with version {version}{tag_info}")
            return version, self.output_dir
        
        except Exception as e:
            print(f"Error building package: {e}")
            raise