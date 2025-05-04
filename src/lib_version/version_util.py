import subprocess
import os 
import json 

class VersionUtil:
    @staticmethod
    def get_version():
        """Get version from git tag or fallback to version file if available."""
        try:
            # Try to get version from git tag
            git_tag = subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
            
            # Remove 'v' prefix if present
            if git_tag.startswith('v'):
                git_tag = git_tag[1:]
            
            return git_tag
        except:
            # Fallback to version.json if available
            version_file = os.path.join(os.path.dirname(__file__), "version.json")
            if os.path.exists(version_file):
                with open(version_file) as f:
                    return json.load(f)["version"]
            
            # Default version if all else fails
            return "0.0.0"

    @staticmethod
    def get_commit_hash():
        """
        Returns the current commit hash (short form).
        """
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "--short", "HEAD"]
            ).decode().strip()
        except subprocess.CalledProcessError:
            return "unknown"

    @staticmethod
    def get_branch():
        """
        Returns the current Git branch.
        """
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"]
            ).decode().strip()
        except subprocess.CalledProcessError:
            return "unknown"

    @staticmethod
    def get_metadata():
        """
        Returns a dictionary with tag, commit hash, and branch.
        """
        return {
            "version": VersionUtil.get_version(),
            "commit": VersionUtil.get_commit_hash(),
            "branch": VersionUtil.get_branch()
        }
