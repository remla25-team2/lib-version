import argparse
import os
import sys
from .builder import PackageBuilder
from .version_util import VersionUtil

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Build packages with automatic versioning"
    )
    
    parser.add_argument(
        "--package-dir", "-p",
        default=".",
        help="Directory containing the package to build (default: current directory)"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        help="Directory to store build artifacts (default: {package_dir}/dist)"
    )
    
    parser.add_argument(
        "--version", "-v",
        help="Override the version instead of using git tags"
    )
    
    parser.add_argument(
        "--no-auto-bump",
        action="store_true",
        help="Disable automatic version bumping for non-tagged commits"
    )
    
    parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not clean the output directory before building"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show version info without building"
    )

    parser.add_argument(
        "--get-bumped-version",
        action="store_true",
        help="Get the bumped patch version from the current version"
    )

    parser.add_argument(
    "--get-next-patch-version",
        nargs=2,
        metavar=("MAJOR", "MINOR"),
        help="Get the next patch version for a given major.minor"
    )
    
    return parser.parse_args()

def main():
    """
    Main entry point for the CLI
    """
    args = parse_arguments()
    
    # Just show version info if requested
    if args.info:
        metadata = VersionUtil.get_metadata()
        print(f"Package version: {metadata['version']}")
        print(f"Git commit: {metadata['commit']}")
        print(f"Git branch: {metadata['branch']}")
        return 0
    
    if args.get_bumped_version:
        current_version = VersionUtil.get_version()
        bumped_version = VersionUtil.bump_patch_version(current_version)
        print(bumped_version)
        return 0
    
    # In the main function:
    if args.get_next_patch_version:
        major, minor = args.get_next_patch_version
        next_version = VersionUtil.get_next_patch_version(major, minor)
        print(next_version)
        return 0
    
    # Create builder
    builder = PackageBuilder(
        package_dir=args.package_dir,
        output_dir=args.output_dir,
        version_override=args.version
    )
    
    # Build the package
    try:
        version, output_dir = builder.build(
            auto_bump=not args.no_auto_bump,
            clean=not args.no_clean
        )
        print(f"Built package version {version} in {output_dir}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())