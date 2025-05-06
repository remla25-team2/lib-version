import pytest
from lib_version.version_util import VersionUtil, VersionPart

def test_parse_version():
    """Test version parsing"""
    assert VersionUtil.parse_version("1.2.3") == (1, 2, 3, None)
    assert VersionUtil.parse_version("v1.2.3") == (1, 2, 3, None)
    assert VersionUtil.parse_version("1.2") == (1, 2, None, None)
    assert VersionUtil.parse_version("v1.2") == (1, 2, None, None)
    assert VersionUtil.parse_version("1.2.3-dev1") == (1, 2, 3, "dev1")
    assert VersionUtil.parse_version("invalid") is None

def test_format_version():
    """Test version formatting"""
    assert VersionUtil.format_version(1, 2, 3) == "1.2.3"
    assert VersionUtil.format_version(1, 2) == "1.2"
    assert VersionUtil.format_version(1, 2, 3, "dev1") == "1.2.3-dev1"
    assert VersionUtil.format_version(1, 2, 3, include_v=True) == "v1.2.3"

def test_bump_version():
    """Test version bumping"""
    assert VersionUtil.bump_version("1.2.3", VersionPart.MAJOR) == "2.0.0"
    assert VersionUtil.bump_version("1.2.3", VersionPart.MINOR) == "1.3.0"
    assert VersionUtil.bump_version("1.2.3", VersionPart.PATCH) == "1.2.4"
    assert VersionUtil.bump_version("1.2", VersionPart.PATCH) == "1.2.1"