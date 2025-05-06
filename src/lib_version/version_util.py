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
            cmd = ["git", "tag", "--sort=-v:refname"]
            if pattern:
                cmd.extend(["-l", pattern])
                
            tags = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").strip().split('\n')
            return tags[0] if tags and tags[0] else None
        except:
            return None
    
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
            
        # Fallback to version.json if available
        version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "version.json")
        print(f"Looking for version file at: {version_file}")
        if os.path.exists(version_file):
            with open(version_file) as f:
                return json.load(f)["version"]
                
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
            
        major, minor, _, _ = parsed
        
        # Find all tags that match this major.minor
        pattern = f"v{major}.{minor}.*"
        matching_tags = VersionUtil.get_all_tags(pattern)
        
        # Extract patch numbers
        patch_versions = []
        for t in matching_tags:
            p = VersionUtil.parse_version(t)
            if p:
                patch_versions.append(p[2])
        
        # Return the next patch version
        next_patch = max(patch_versions) + 1 if patch_versions else 0
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
        return {
            "version": VersionUtil.get_version(),
            "commit": VersionUtil.get_commit_hash(),
            "branch": VersionUtil.get_branch(),
            "timestamp": subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S"]).decode().strip()
        }
    
    @staticmethod
    def _save_version(version):
        """Save the version to version.json"""
        metadata = {
            "version": version,
            "commit": VersionUtil.get_commit_hash(),
            "branch": VersionUtil.get_branch(),
            "timestamp": subprocess.check_output(["date", "+%Y-%m-%d %H:%M:%S"]).decode().strip()
        }
        
        with open("version.json", "w") as f:
            json.dump(metadata, f, indent=2)