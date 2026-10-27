"""Tests for app/services/auth_service.py (Roadmap Tasks T2.6 and T2.12).

Tests use a temporary folder (Rules 29) and a fake clock, so the 5-minute lock can be checked.
"""

from datetime import datetime, timedelta

import pytest

from app.core import config
from app.services import auth_service
from app.services.auth_service import AuthService
from app.storage.account_store import AccountStore, CorruptAccountFileError


class FakeClock:
    """A clock the test moves forward by hand."""

    def __init__(self, start: datetime) -> None:
        self.now = start

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs) -> None:
        self.now += timedelta(**kwargs)


@pytest.fixture
def clock():
    return FakeClock(datetime(2026, 10, 24, 9, 0, 0))


@pytest.fixture
def service(tmp_path, clock):
    return AuthService(AccountStore(tmp_path / "account.json"), clock=clock)


@pytest.fixture
def account(service):
    result = service.create_account("owner", "secret123", "secret123")
    assert result.ok
    return service


def fail_login(service, times):
    for _ in range(times):
        service.login("owner", "not-the-password")


def test_create_account_saves_hash_not_plain_password(service, tmp_path):
    assert service.create_account("owner", "secret123", "secret123").ok
    saved = (tmp_path / "account.json").read_text(encoding="utf-8")
    assert "secret123" not in saved
    assert service.has_account()


def test_create_account_refuses_second_account(account):
    result = account.create_account("other", "secret123", "secret123")
    assert not result.ok
    assert result.message == "An account already exists."


@pytest.mark.parametrize(
    "username, password, repeat, message",
    [
        ("", "secret123", "secret123", "Username is required."),
        ("owner", "short", "short", "Use at least 8 characters."),
        ("owner", "secret123", "secret124", "Passwords do not match."),
    ],
)
def test_create_account_validation(service, username, password, repeat, message):
    result = service.create_account(username, password, repeat)
    assert not result.ok
    assert result.message == message


def test_correct_login_passes(account):
    assert account.login("owner", "secret123").ok


def test_four_wrong_then_correct_login_passes(account):
    fail_login(account, 4)
    assert account.login("owner", "secret123").ok


def test_wrong_login_shows_tries_left(account):
    result = account.login("owner", "wrong")
    assert result.message == "Wrong username or password. 4 tries left."


def test_five_wrong_logins_lock(account):
    fail_login(account, 5)
    assert account.lock_remaining_seconds() == config.LOCK_MINUTES * 60
    result = account.login("owner", "secret123")
    assert not result.ok
    assert result.message.startswith("Too many attempts.")


def test_lock_survives_a_new_service_object(account, tmp_path, clock):
    fail_login(account, 5)
    restarted = AuthService(AccountStore(tmp_path / "account.json"), clock=clock)
    assert restarted.lock_remaining_seconds() > 0
    assert not restarted.login("owner", "secret123").ok


def test_lock_expires_after_five_minutes(account, clock):
    fail_login(account, 5)
    clock.advance(minutes=5, seconds=1)
    assert account.lock_remaining_seconds() == 0
    assert account.login("owner", "secret123").ok


def test_lock_message_format(account, clock):
    fail_login(account, 5)
    clock.advance(seconds=48)
    assert account.login("owner", "secret123").message == "Too many attempts. Try again in 4 min 12 sec."


def test_corrupt_account_file_is_reported_not_overwritten(tmp_path, clock):
    path = tmp_path / "account.json"
    path.write_text("{ not json", encoding="utf-8")
    service = AuthService(AccountStore(path), clock=clock)
    with pytest.raises(CorruptAccountFileError):
        service.login("owner", "secret123")
    assert path.read_text(encoding="utf-8") == "{ not json"


# ---- Change password (T2.11, T2.12) ----

def test_change_password_then_new_password_logs_in(account):
    assert account.change_password("secret123", "newpass456", "newpass456").ok
    assert account.login("owner", "newpass456").ok
    assert not account.login("owner", "secret123").ok


def test_change_password_wrong_current_counts_toward_lock(account, clock):
    for _ in range(4):
        result = account.change_password("wrong", "newpass456", "newpass456")
    assert result.message == "Wrong current password. 1 tries left."
    result = account.change_password("wrong", "newpass456", "newpass456")
    assert result.message.startswith("Too many attempts.")
    assert account.lock_remaining_seconds() == config.LOCK_MINUTES * 60


def test_change_password_rejects_short_new_password(account):
    result = account.change_password("secret123", "short", "short")
    assert result.message == "Use at least 8 characters."


def test_change_password_rejects_same_password(account):
    result = account.change_password("secret123", "secret123", "secret123")
    assert result.message == "The new password must be different from the current one."


def test_change_password_rejects_mismatched_confirmation(account):
    result = account.change_password("secret123", "newpass456", "newpass457")
    assert result.message == "Passwords do not match."


def test_change_password_is_refused_while_locked(account):
    fail_login(account, 5)
    result = account.change_password("secret123", "newpass456", "newpass456")
    assert result.message.startswith("Too many attempts.")


def test_change_password_resets_failed_count(account):
    fail_login(account, 3)
    assert account.change_password("secret123", "newpass456", "newpass456").ok
    result = account.login("owner", "wrong")
    assert result.message == "Wrong username or password. 4 tries left."


def test_format_lock_message_pads_seconds():
    assert auth_service.format_lock_message(65) == "Too many attempts. Try again in 1 min 05 sec."
