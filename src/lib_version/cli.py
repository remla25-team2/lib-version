import argparse
import os
import sys
from .builder import PackageBuilder
from .version_util import VersionUtil, VersionPart

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Build packages with automatic versioning"
    )
    
    # Main build command
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
        "--no-clean",
        action="store_true",
        help="Do not clean the output directory before building"
    )
    
    # Info commands
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show version info without building"
    )

    # Version management commands
    parser.add_argument(
        "--bump",
        choices=["major", "minor", "patch"],
        help="Bump the specified version part and create a new tag"
    )
    
    parser.add_argument(
        "--create-tag",
        help="Create a new git tag with the specified version"
    )

    parser.add_argument(
        "--get-version",
        action="store_true",
        help="Get the current version"
    )

    parser.add_argument(
        "--get-next-version",
        action="store_true",
        help="Get the next version based on the current version"
    )

    parser.add_argument(
        "--get-next-patch-version",
        nargs=2,
        metavar=("MAJOR", "MINOR"),
        help="Get the next patch version for a given major.minor"
    )

    parser.add_argument(
        "--get-dev-version",
        action="store_true",
        help="Get the next version in development format"
    )
    
    parser.add_argument(
        "--push",
        action="store_true",
        help="Push created tags to remote"
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
    
    # Version getters
    if args.get_version:
        print(VersionUtil.get_version())
        return 0
        
    if args.get_next_version:
        version = VersionUtil.get_version()
        next_version = VersionUtil.bump_version(version, VersionPart.PATCH)
        print(next_version)
        return 0
    
    if args.get_next_patch_version:
        major, minor = args.get_next_patch_version
        tag = f"v{major}.{minor}"
        next_version = VersionUtil.get_next_version_for_tag(tag)
        print(next_version)
        return 0
    
    if args.get_dev_version:
        print(VersionUtil.get_dev_version())
        return 0
    
    # Version management
    if args.bump:
        version = VersionUtil.get_version()
        part = {"major": VersionPart.MAJOR, "minor": VersionPart.MINOR, "patch": VersionPart.PATCH}[args.bump]
        next_version = VersionUtil.bump_version(version, part)
        success = VersionUtil.create_tag(next_version, args.push)
        if success:
            print(next_version)
            return 0
        return 1
    
    if args.create_tag:
        success = VersionUtil.create_tag(args.create_tag, args.push)
        return 0 if success else 1
    
    # Create builder
    builder = PackageBuilder(
        package_dir=args.package_dir,
        output_dir=args.output_dir,
        version_override=args.version
    )
    
    # Build the package
    try:
        version, output_dir = builder.build(
            clean=not args.no_clean
        )
        print(f"Built package version {version} in {output_dir}")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())