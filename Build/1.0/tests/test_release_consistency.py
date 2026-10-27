"""Guards for upgrades: the version is set in one place, and the codes that let Windows upgrade stay fixed."""

import re
from pathlib import Path

from app.core import config

BUILD = Path(__file__).resolve().parents[1]
ROOT = BUILD.parents[1]

# These must never change, or Windows stops treating a new version as an upgrade of the old one.
MSI_UPGRADE_CODE = "6F1E2B7A-4C3D-4E8F-9A10-2B3C4D5E6F70"
BUNDLE_UPGRADE_CODE = "7A1C0E2D-5B3F-4D6A-8E9F-1A2B3C4D5E60"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_upgrade_codes_never_change():
    assert f'UpgradeCode="{MSI_UPGRADE_CODE}"' in read(BUILD / "installer" / "Product.wxs")
    assert f'UpgradeCode="{BUNDLE_UPGRADE_CODE}"' in read(BUILD / "installer" / "Bundle.wxs")


def test_installers_take_the_version_from_the_build():
    assert 'Version="$(var.AppVersion)"' in read(BUILD / "installer" / "Product.wxs")
    assert 'Version="$(var.AppVersion).0"' in read(BUILD / "installer" / "Bundle.wxs")


def test_major_upgrade_is_on():
    assert "<MajorUpgrade" in read(BUILD / "installer" / "Product.wxs")


def test_version_is_dotted_numbers():
    assert re.fullmatch(r"\d+\.\d+\.\d+", config.APP_VERSION)


def test_exe_properties_match_the_app_version():
    text = read(BUILD / "version_info.txt")
    four = config.APP_VERSION + ".0"
    assert f"u'FileVersion', u'{four}'" in text
    assert f"u'ProductVersion', u'{four}'" in text
    assert f"filevers=({four.replace('.', ', ')})" in text


def test_changelog_has_an_entry_for_this_version():
    assert re.search(rf"^## {re.escape(config.APP_VERSION)}\b", read(ROOT / "CHANGELOG.md"), re.MULTILINE)
