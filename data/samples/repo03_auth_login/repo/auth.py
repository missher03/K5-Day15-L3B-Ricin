import hashlib
import hmac
import os
import time

ITERATIONS = 200_000
MAX_ATTEMPTS = 5
LOCK_SECONDS = 300
_failed = {}


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, ITERATIONS)
    return salt.hex() + "$" + digest.hex()


def verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split("$", 1)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt_hex), ITERATIONS)
    return hmac.compare_digest(digest.hex(), digest_hex)


def login(username: str, password: str, users: dict) -> bool:
    count, since = _failed.get(username, (0, 0.0))
    if count >= MAX_ATTEMPTS and time.monotonic() - since < LOCK_SECONDS:
        raise PermissionError("tài khoản tạm khoá, thử lại sau")
    stored = users.get(username)
    if stored is None or not verify_password(password, stored):
        _failed[username] = (count + 1, time.monotonic())
        return False
    _failed.pop(username, None)
    return True
