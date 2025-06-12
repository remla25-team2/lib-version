import subprocess
import os 
import json
import re
from enum import Enum

class VersionPart(Enum):
    MAJOR = 0
    MINOR = 1
    PATCH = 2

class VersionUtil:
    VERSION_PATTERN = r"^v?(\d+)\.(\d+)(?:\.(\d+))?(?:-([a-zA-Z0-9.-]+))?$"
    
    @staticmethod
    def parse_version(version_str):
        """Parse version string into components (major, minor, patch, prerelease)."""
        if not version_str:
            return None
            
        match = re.match(VersionUtil.VERSION_PATTERN, version_str)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3)) if match.group(3) else None
            prerelease = match.group(4) if match.group(4) else None
            return (major, minor, patch, prerelease)
        return None
    
    @staticmethod
    def format_version(major, minor, patch=None, prerelease=None, include_v=False):
        """Format version components into a string."""
        if patch is None:
            version = f"{major}.{minor}"
        else:
            version = f"{major}.{minor}.{patch}"
            
        if prerelease:
            version += f"-{prerelease}"
            
        if include_v:
            version = f"v{version}"
            
        return version
    
    @staticmethod
    def get_latest_tag(pattern=None):
        """Get the latest tag from git, optionally matching a pattern."""
        try:
            cmd = ["git", "tag"]
            if pattern:
                cmd.extend(["-l", pattern])
                
            tags = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip().split('\n')
            tags = [t for t in tags if t]
            
            if not tags:
                return None
            
            # Parse all tags and filter out invalid ones
            parsed_tags = []
            for tag in tags:
                parsed = VersionUtil.parse_version(tag)
                if parsed:
                    # Store tuple of (tag, parsed_version)
                    parsed_tags.append((tag, parsed))
            
            if not parsed_tags:
                return None
                
            # First find highest non-pre-release version
            non_pre_tags = [(tag, parsed) for tag, parsed in parsed_tags if parsed[3] is None]
            if non_pre_tags:
                # Sort by major, minor, patch (where patch might be None)
                # Ensure explicit patch versions (0.1.0) are considered higher than implicit (0.1)
                sorted_tags = sorted(non_pre_tags, key=lambda x: (
                    x[1][0],                         # major
                    x[1][1],                         # minor
                    -1 if x[1][2] is None else x[1][2]  # patch (None treated as lower than 0)
                ), reverse=True)
                return sorted_tags[0][0]
            
            # If only pre-release versions exist, use the highest one but strip -pre
            sorted_tags = sorted(parsed_tags, key=lambda x: (
                x[1][0],                         # major
                x[1][1],                         # minor
                -1 if x[1][2] is None else x[1][2]  # patch (None treated as lower than 0)
            ), reverse=True)
            
            if sorted_tags:
                tag = sorted_tags[0][0]
                return tag.replace("-pre", "")
                
            return None
        except Exception as e:
            print(f"Error getting latest tag: {e}")
            return None
        
    @staticmethod
    def delete_tag(tag, push=False):
        """Delete a git tag and optionally push the deletion."""
        try:
            # Delete local tag
            subprocess.check_call(["git", "tag", "-d", tag])
            print(f"Deleted local tag: {tag}")
            
            # Push deletion if requested
            if push:
                subprocess.check_call(["git", "push", "origin", f":refs/tags/{tag}"])
                print(f"Pushed tag deletion: {tag}")
                
            return True
        except Exception as e:
            print(f"Error deleting tag: {e}")
            return False
    
    @staticmethod
    def get_all_tags(pattern=None):
        """Get all tags from git, optionally matching a pattern."""
        try:
            cmd = ["git", "tag"]
            if pattern:
                cmd.extend(["-l", pattern])
                
            tags = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip().split('\n')
            return [t for t in tags if t]
        except:
            return []
    
    @staticmethod
    def get_version():
        """Get version from git tag or fallback to version file."""
        try:
            # Try to get latest tag
            latest_tag = VersionUtil.get_latest_tag()
            if latest_tag:
                # Strip 'v' prefix if present for use in package version
                version = latest_tag[1:] if latest_tag.startswith('v') else latest_tag
                VersionUtil._save_version(version)
                return version
        except:
            pass
                
        try:
            from ._version import __version__
            return __version__
        except ImportError:
            # Default version if all else fails
            print("No version found, returning default version.")
            return "0.0.1-dev0"
    
    @staticmethod
    def bump_version(version, part=VersionPart.PATCH):
        """Bump specified part of the version."""
        parsed = VersionUtil.parse_version(version)
        if not parsed:
            return version
            
        major, minor, patch, prerelease = parsed
        
        if part == VersionPart.MAJOR:
            return VersionUtil.format_version(major + 1, 0, 0)
        elif part == VersionPart.MINOR:
            return VersionUtil.format_version(major, minor + 1, 0)
        else:  # PATCH
            if patch is None:
                patch = 0
            return VersionUtil.format_version(major, minor, patch + 1)
    
    @staticmethod
    def get_next_version_for_tag(tag):
        """Get the next version based on a vX.Y style tag."""
        parsed = VersionUtil.parse_version(tag)
        if not parsed:
            return None
            
        major, minor, patch, _ = parsed
        
        # Increment patch version
        if patch is None:
            patch = 0
        next_patch = patch + 1
        # Format the next version
        return VersionUtil.format_version(major, minor, next_patch)
    
    @staticmethod
    def is_on_tagged_commit():
        """Check if the current commit has a tag."""
        try:
            subprocess.check_output(
                ["git", "describe", "--exact-match", "--tags"],
                stderr=subprocess.DEVNULL
            )
            return True
        except:
            return False
    
    @staticmethod
    def create_tag(version, push=False):
        """Create a new git tag and optionally push it."""
        tag = f"v{version}" if not version.startswith('v') else version
        
        try:
            # Create the tag
            subprocess.check_call(["git", "tag", tag])
            print(f"Created tag: {tag}")
            
            # Push if requested
            if push:
                subprocess.check_call(["git", "push", "origin", tag])
                print(f"Pushed tag: {tag}")
                
            return True
        except Exception as e:
            print(f"Error creating tag: {e}")
            return False
    
    @staticmethod
    def get_dev_version(base_version=None):
        """Generate a PEP 440 compliant development version."""
        if not base_version:
            # Try to get latest tag as base
            latest_tag = VersionUtil.get_latest_tag()
            if latest_tag:
                base_version = latest_tag[1:] if latest_tag.startswith('v') else latest_tag
            else:
                base_version = "0.0.1"
        
        try:
            # Get number of commits since last tag
            commit_count = subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD"],
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
            
            # Get branch name and commit hash
            branch = VersionUtil.get_branch()
            commit_hash = VersionUtil.get_commit_hash()
            
            # Format dev version: base.dev{commit_count}+{branch}.{commit_hash}
            branch_info = branch.replace("/", ".") if branch != "HEAD" else "unknown"
            dev_version = f"{base_version}.dev{commit_count}+{branch_info}.{commit_hash}"
            
            VersionUtil._save_version(dev_version)
            return dev_version
        except:
            # Fallback if git commands fail
            return f"{base_version}.dev0"
    
    @staticmethod
    def get_commit_hash():
        """Returns the current commit hash (short form)."""
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"]
            ).decode().strip()
        except:
            return "unknown"

    @staticmethod
    def get_branch():
        """Returns the current Git branch."""
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"]
            ).decode().strip()
        except:
            return "unknown"

    @staticmethod
    def get_metadata():
        """Returns a dictionary with version metadata."""

        timestamp_raw = subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S"]).decode().strip()

        # Format timestamp for use in versions/metadata - replace spaces and colons with hyphens
        timestamp_clean = timestamp_raw.replace(" ", "-").replace(":", "-")

        return {
            "version": VersionUtil.get_version(),
            "commit": VersionUtil.get_commit_hash(),
            "branch": VersionUtil.get_branch(),
            "timestamp": timestamp_clean
        }
    
    @staticmethod
    def _save_version(version):
        """Save the version to version.json"""

        timestamp_raw = subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S"]).decode().strip()
        # Format timestamp
        timestamp_clean = timestamp_raw.replace(" ", "-").replace(":", "-")
        metadata = {
            "version": version,
            "commit": VersionUtil.get_commit_hash(),
            "branch": VersionUtil.get_branch(),
            "timestamp": timestamp_clean        }
        
        with open("version.json", "w") as f:
            json.dump(metadata, f, indent=2)

    @staticmethod
    def get_major_minor_tags():
        """Get all major.minor tags."""
        tags = VersionUtil.get_all_tags()
        major_minor_tags = []
        
        for tag in tags:
            parsed = VersionUtil.parse_version(tag)
            if parsed and parsed[2] is None:
                # Only include major.minor tags
                major_minor_tags.append(tag)
        return major_minor_tags