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
        
            # save version to version.json
            VersionUtil._save_version(git_tag)
            return git_tag
        except:
            # Fallback to version.json if available
            version_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "version.json")
            if os.path.exists(version_file):
                with open(version_file) as f:
                    return json.load(f)["version"]
                
            # Default version if all else fails
            print("No version found, returning default version.")
            return "0.0.0"
        
    @staticmethod
    def bump_patch_version(version):
        """
        Bump the patch version of a semantic version string.
        Example: '1.2.3' -> '1.2.4'
        """
        import re
        pattern = r"^v?(\d+)\.(\d+)\.(\d+)(?:\.(.+)|-(.*)|$)"
        match = re.match(pattern, version)
        if match:
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3))
            # Bump patch
            patch += 1
            # Return new version without v prefix
            return f"{major}.{minor}.{patch}"
        return version
    

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
    
    @staticmethod
    def _save_version(version):
        """
        Save the version to version.json
        """
        metadata = {
            "version": version,
            "commit": VersionUtil.get_commit_hash(),
            "branch": VersionUtil.get_branch()
        }
        
        with open("version.json", "w") as f:
            json.dump(metadata, f, indent=2)


    @staticmethod
    def get_dev_version(base_version="0.0.1"):
        """
        Generate a PEP 440 compliant development version.
        For non-tagged commits, we use: {base}.dev{commit_count}+{commit_hash}
        """
        try:
            # Get number of commits since last tag
            commit_count = subprocess.check_output(
                ["git", "rev-list", "--count", "HEAD"],
                stderr=subprocess.DEVNULL
            ).decode("utf-8").strip()
            
            # Get commit hash
            commit_hash = VersionUtil.get_commit_hash()
            
            # Format according to PEP 440
            dev_version = f"{base_version}.dev{commit_count}+{commit_hash}"
            
            # Save version
            VersionUtil._save_version(dev_version)
            return dev_version
        except:
            # Fallback if git commands fail
            return f"{base_version}.dev0"
