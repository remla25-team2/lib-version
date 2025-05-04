import subprocess

class VersionUtil:
    @staticmethod
    def get_version():
        """
        Returns the latest Git tag, or falls back to short commit hash.
        """
        try:
            version = subprocess.check_output(
                ["git", "describe", "--tags", "--abbrev=0"],
                stderr=subprocess.DEVNULL
            ).decode().strip()
        except subprocess.CalledProcessError:
            version = VersionUtil.get_commit_hash()
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
