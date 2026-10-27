"""Tests for app/services/password_hash.py (Roadmap Tasks T2.2)."""

from app.services import password_hash

FAST_ITERATIONS = 1000  # keeps the tests quick; the app uses config.PBKDF2_ITERATIONS


def test_correct_password_passes():
    digest, salt = password_hash.hash_password("correct-horse", FAST_ITERATIONS)
    assert password_hash.check_password("correct-horse", digest, salt, FAST_ITERATIONS)


def test_wrong_password_fails():
    digest, salt = password_hash.hash_password("correct-horse", FAST_ITERATIONS)
    assert not password_hash.check_password("wrong-password", digest, salt, FAST_ITERATIONS)


def test_same_password_gives_different_hashes_because_of_salt():
    first = password_hash.hash_password("same-password", FAST_ITERATIONS)
    second = password_hash.hash_password("same-password", FAST_ITERATIONS)
    assert first[0] != second[0]
    assert first[1] != second[1]


def test_hash_does_not_contain_plain_password():
    digest, salt = password_hash.hash_password("visible-text", FAST_ITERATIONS)
    assert "visible-text" not in digest
    assert "visible-text" not in salt
