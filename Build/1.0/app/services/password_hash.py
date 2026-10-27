"""Password hashing with PBKDF2-SHA256 from the standard library (PRD FR-3, NFR-5, Rules 19 and 20).

Plain passwords are never stored, logged, or printed. Only the hash and the salt are saved.
"""

import hashlib
import hmac
import secrets

from app.core import config

SALT_BYTES = 16


def hash_password(password: str, iterations: int = config.PBKDF2_ITERATIONS) -> tuple[str, str]:
    """Return (hash, salt) as hex text. A new random salt is used every time."""
    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return digest.hex(), salt.hex()


def check_password(password: str, password_hash: str, salt: str, iterations: int) -> bool:
    """Return True if the password matches the stored hash. The comparison takes the same time either way."""
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), iterations)
    return hmac.compare_digest(digest.hex(), password_hash)
