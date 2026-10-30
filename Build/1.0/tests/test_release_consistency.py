"""Guards for upgrades: the version is set in one place, and the codes that let Windows upgrade stay fixed."""

import re
from pathlib import Path

from app.core import config

BUILD = Path(__file__).resolve().parents[1]
ROOT = BUILD.parents[1]

# These must never change, or Windows stops treating a new version as an upgrade of the old one.
MSI_UPGRADE_CODE = "6F1E2B7A-4C3D-4E8F-9A10-2B3C4D5E6F70"
SETUP_APP_ID = "B7F3A9E2-6C41-4D58-9E0A-3F5C1D7A8B24"  # the setup wizard (Inno Setup)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_upgrade_codes_never_change():
    assert f'UpgradeCode="{MSI_UPGRADE_CODE}"' in read(BUILD / "installer" / "Product.wxs")
    assert "AppId={{" + SETUP_APP_ID + "}" in read(BUILD / "installer" / "DailyFresh.iss")


def test_installers_take_the_version_from_the_build():
    assert 'Version="$(var.AppVersion)"' in read(BUILD / "installer" / "Product.wxs")
    assert "AppVersion={#AppVersion}" in read(BUILD / "installer" / "DailyFresh.iss")


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


def test_setup_wizard_trust_option_points_at_the_shipped_certificate():
    """The thumbprint shown in the wizard and used to remove the certificate must be the one in the .cer file."""
    import hashlib
    import re
    import ssl

    script = read(BUILD / "installer" / "DailyFresh.iss")
    thumbprint = re.search(r'#define CertThumbprint "([0-9A-F]{40})"', script).group(1)
    der = ssl.PEM_cert_to_DER_cert((BUILD / "installer" / "TenwinJames-CodeSigning.cer").read_text()) if b"BEGIN" in (BUILD / "installer" / "TenwinJames-CodeSigning.cer").read_bytes() else (BUILD / "installer" / "TenwinJames-CodeSigning.cer").read_bytes()
    assert hashlib.sha1(der).hexdigest().upper() == thumbprint
