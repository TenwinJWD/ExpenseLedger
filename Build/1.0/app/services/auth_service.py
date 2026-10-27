"""Account rules: create the account, log in, lock after failures, and change the password.

PRD FR-2, FR-4, FR-37 to FR-41. The clock is passed in so the lock can be tested.
Messages are plain text for the screens (PRD FR-16, Rules 26).
"""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Callable

from app.core import config
from app.services import password_hash
from app.storage.account_store import AccountStore


@dataclass
class Result:
    """Outcome of an action. message is empty when ok is True."""

    ok: bool
    message: str = ""


def format_lock_message(seconds: int) -> str:
    """Return the lock message shown on the login and Change Password screens."""
    minutes, rest = divmod(seconds, 60)
    return f"Too many attempts. Try again in {minutes} min {rest:02d} sec."


class AuthService:
    """Owns the rules for the single account on this PC."""

    def __init__(self, store: AccountStore, clock: Callable[[], datetime] = datetime.now) -> None:
        self.store = store
        self.clock = clock

    def has_account(self) -> bool:
        return self.store.exists()

    def create_account(self, username: str, password: str, repeat: str) -> Result:
        """Create the one account. Refuses if an account already exists (FR-2)."""
        if self.store.exists():
            return Result(False, "An account already exists.")
        username = username.strip()
        if not username:
            return Result(False, "Username is required.")
        if len(password) < config.MIN_PASSWORD_LENGTH:
            return Result(False, f"Use at least {config.MIN_PASSWORD_LENGTH} characters.")
        if password != repeat:
            return Result(False, "Passwords do not match.")
        password_text, salt = password_hash.hash_password(password)
        self.store.save({
            "username": username,
            "password_hash": password_text,
            "salt": salt,
            "iterations": config.PBKDF2_ITERATIONS,
            "failed_attempts": 0,
            "locked_until": None,
        })
        return Result(True)

    def lock_remaining_seconds(self) -> int:
        """Seconds left on the lock, rounded up. Zero when not locked."""
        data = self.store.load()
        if data is None or not data["locked_until"]:
            return 0
        remaining = datetime.fromisoformat(data["locked_until"]) - self.clock()
        return max(0, math.ceil(remaining.total_seconds()))

    def login(self, username: str, password: str) -> Result:
        """Check the username and password. Five wrong tries lock the login (FR-4)."""
        data = self.store.load()
        if data is None:
            return Result(False, "No account exists yet.")
        locked_for = self.lock_remaining_seconds()
        if locked_for > 0:
            return Result(False, format_lock_message(locked_for))

        matches = username.strip() == data["username"] and password_hash.check_password(
            password, data["password_hash"], data["salt"], data["iterations"])
        if matches:
            data["failed_attempts"] = 0
            data["locked_until"] = None
            self.store.save(data)
            return Result(True)
        return self._record_failure(data, "Wrong username or password.")

    def change_password(self, current: str, new: str, repeat: str) -> Result:
        """Replace the password after checking the current one (FR-39 to FR-41)."""
        data = self.store.load()
        if data is None:
            return Result(False, "No account exists yet.")
        locked_for = self.lock_remaining_seconds()
        if locked_for > 0:
            return Result(False, format_lock_message(locked_for))

        if not password_hash.check_password(current, data["password_hash"], data["salt"], data["iterations"]):
            return self._record_failure(data, "Wrong current password.")
        if len(new) < config.MIN_PASSWORD_LENGTH:
            return Result(False, f"Use at least {config.MIN_PASSWORD_LENGTH} characters.")
        if new == current:
            return Result(False, "The new password must be different from the current one.")
        if new != repeat:
            return Result(False, "Passwords do not match.")

        password_text, salt = password_hash.hash_password(new)
        data.update({
            "password_hash": password_text,
            "salt": salt,
            "iterations": config.PBKDF2_ITERATIONS,
            "failed_attempts": 0,
            "locked_until": None,
        })
        self.store.save(data)
        return Result(True)

    def _record_failure(self, data: dict, wrong_message: str) -> Result:
        """Count one wrong try. At the limit, start the lock and reset the count."""
        data["failed_attempts"] += 1
        if data["failed_attempts"] >= config.MAX_LOGIN_ATTEMPTS:
            lock_until = self.clock() + timedelta(minutes=config.LOCK_MINUTES)
            data["locked_until"] = lock_until.isoformat()
            data["failed_attempts"] = 0
            self.store.save(data)
            return Result(False, format_lock_message(config.LOCK_MINUTES * 60))
        self.store.save(data)
        left = config.MAX_LOGIN_ATTEMPTS - data["failed_attempts"]
        return Result(False, f"{wrong_message} {left} tries left.")
