import argparse
import os
import sys
from .builder import PackageBuilder
from .version_util import VersionUtil, VersionPart

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Build packages with automatic versioning"
    )

    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build package with automatic versioning")
    build_parser.add_argument(
        "--package-dir", "-p",
        default=".",
        help="Directory containing the package to build (default: current directory)"
    )
    build_parser.add_argument(
        "--output-dir", "-o",
        help="Directory to store build artifacts (default: {package_dir}/dist)"
    )
    build_parser.add_argument(
        "--version", "-v",
        help="Override the version instead of using git tags"
    )
    build_parser.add_argument(
        "--no-clean",
        action="store_true",
        help="Do not clean the output directory before building"
    )
    build_parser.add_argument(
        "--dev",
        action="store_true",
        help="Build with development version (PEP 440 compliant) for untagged commits"
    )

    # Info command
    subparsers.add_parser("info", help="Show version info without building")

    # Version commands
    version_parser = subparsers.add_parser("version", help="Version information commands")
    version_subparsers = version_parser.add_subparsers(dest="version_command", help="Version command to execute")

    # Current version
    version_subparsers.add_parser("current", help="Get the current version")

    # Next version
    version_subparsers.add_parser("next", help="Get the next version based on the current version")

    # Dev version
    version_subparsers.add_parser("dev", help="Get the next version in development format")

    # Metadata command
    version_subparsers.add_parser("metadata", help="Get version metadata (version, commit, branch, timestamp)")

    # Next patch version
    next_patch_parser = version_subparsers.add_parser("next-patch", help="Get the next patch version for a given major.minor")
    next_patch_parser.add_argument("major", type=int, help="Major version number")
    next_patch_parser.add_argument("minor", type=int, help="Minor version number")

    # Bump command
    bump_parser = subparsers.add_parser("bump", help="Bump version and create a tag")
    bump_parser.add_argument("part", choices=["major", "minor", "patch"], help="Version part to bump")
    bump_parser.add_argument(
        "--push",
        action="store_true",
        help="Push created tag to remote"
    )

    # Tag command
    tag_parser = subparsers.add_parser("tag", help="Create a new git tag")
    tag_parser.add_argument("version", help="Version to tag")
    tag_parser.add_argument(
        "--push",
        action="store_true",
        help="Push created tag to remote"
    )


    return parser.parse_args()

def main():
    """
    Main entry point for the CLI
    """
    args = parse_arguments()

    # Handle commands
    if args.command == "info":
        metadata = VersionUtil.get_metadata()
        print(f"Package version: {metadata['version']}")
        print(f"Git commit: {metadata['commit']}")
        print(f"Git branch: {metadata['branch']}")
        print(f"Timestamp: {metadata['timestamp']}")
        return 0

    elif args.command == "version":
        if args.version_command == "current":
            print(VersionUtil.get_version())
            return 0

        elif args.version_command == "next":
            version = VersionUtil.get_version()
            next_version = VersionUtil.bump_version(version, VersionPart.PATCH)
            print(next_version)
            return 0

        elif args.version_command == "dev":
            print(VersionUtil.get_dev_version())
            return 0
            
        elif args.version_command == "metadata":
            metadata = VersionUtil.get_metadata()
            # Output in a format that's easy to parse in shell scripts
            print(f"version={metadata['version']}")
            print(f"commit={metadata['commit']}")
            print(f"branch={metadata['branch']}")
            print(f"timestamp={metadata['timestamp']}")
            return 0
            
        elif args.version_command == "next-patch":
            tag = f"v{args.major}.{args.minor}"
            next_version = VersionUtil.get_next_version_for_tag(tag)
            print(next_version)
            return 0
            
        else:
            print("Error: Please specify a version subcommand.")
            return 1

    elif args.command == "bump":
        version = VersionUtil.get_version()
        part = {"major": VersionPart.MAJOR, "minor": VersionPart.MINOR, "patch": VersionPart.PATCH}[args.part]
        next_version = VersionUtil.bump_version(version, part)
        success = VersionUtil.create_tag(next_version, args.push)
        if success:
            print(next_version)
            return 0
        return 1

    elif args.command == "tag":
        success = VersionUtil.create_tag(args.version, args.push)
        return 0 if success else 1

    elif args.command == "build":
        # Create builder
        builder = PackageBuilder(
            package_dir=args.package_dir,
            output_dir=args.output_dir,
            version_override=args.version
        )

        # Build the package
        try:
            version, output_dir = builder.build(
                clean=not args.no_clean,
                use_dev_version=args.dev
            )
            print(f"Built package version {version} in {output_dir}")
            return 0
        except Exception as e:
            print(f"Error: {e}")
            return 1

    else:
        print("Error: Please specify a command. Use --help for available commands.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
