import json

from app.services import update_service as us


def manifest(**fields):
    data = {"version": "1.1.0", "url": "https://example.com/setup.exe", "notes": "New things"}
    data.update(fields)
    return json.dumps(data)


def test_version_comparison_is_numeric_not_text():
    assert us.is_newer("1.10.0", "1.9.0")
    assert us.is_newer("1.0.1", "1.0.0")
    assert us.is_newer("2.0", "1.9.9")
    assert not us.is_newer("1.0.0", "1.0.0")
    assert not us.is_newer("1.0", "1.0.0")
    assert not us.is_newer("0.9.0", "1.0.0")


def test_bad_version_text_is_never_newer():
    assert not us.is_newer("latest", "1.0.0")
    assert not us.is_newer("", "1.0.0")
    assert not us.is_newer("1.0.0", "x")


def test_a_newer_version_is_reported():
    info = us.parse_manifest(manifest(), "1.0.0")
    assert info == us.UpdateInfo("1.1.0", "https://example.com/setup.exe", "New things")


def test_same_or_older_version_gives_no_update():
    assert us.parse_manifest(manifest(version="1.0.0"), "1.0.0") is None
    assert us.parse_manifest(manifest(version="0.9.0"), "1.0.0") is None


def test_downloads_must_be_https():
    assert us.parse_manifest(manifest(url="http://example.com/setup.exe"), "1.0.0") is None
    assert us.parse_manifest(manifest(url="file:///c:/x.exe"), "1.0.0") is None


def test_malformed_files_give_no_update():
    for raw in ("not json", "[]", "{}", json.dumps({"version": 2, "url": "https://x"}), b"\xff\xfe"):
        assert us.parse_manifest(raw, "1.0.0") is None


def test_long_notes_are_cut():
    info = us.parse_manifest(manifest(notes="x" * 1000), "1.0.0")
    assert len(info.notes) == 300


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return self.body[:limit]


def test_check_reads_the_file_and_compares():
    opener = lambda url, timeout: FakeResponse(manifest().encode())
    assert us.check_for_update("https://example.com/v.json", "1.0.0", opener=opener).version == "1.1.0"


def test_check_survives_no_internet():
    def opener(url, timeout):
        raise OSError("no network")

    assert us.check_for_update("https://example.com/v.json", "1.0.0", opener=opener) is None


def test_check_never_connects_without_an_https_address():
    def opener(url, timeout):
        raise AssertionError("must not connect")

    assert us.check_for_update("", "1.0.0", opener=opener) is None
    assert us.check_for_update("http://example.com/v.json", "1.0.0", opener=opener) is None
