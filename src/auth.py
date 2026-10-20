import os
import time

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

_ph = PasswordHasher()
ALGO = "HS256"
TOKEN_SECONDS = 7 * 24 * 3600


def _secret():
    s = os.getenv("JWT_SECRET")
    if not s or len(s) < 32:
        raise RuntimeError("Set JWT_SECRET in .env (at least 32 characters)")
    return s


def hash_password(password):
    return _ph.hash(password)


def verify_password(password, hashed):
    try:
        return _ph.verify(hashed, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def make_token(user_id, now=None):
    now = int(now or time.time())
    payload = {"sub": str(user_id), "iat": now, "exp": now + TOKEN_SECONDS}
    return jwt.encode(payload, _secret(), algorithm=ALGO)


def read_token(token):
    try:
        data = jwt.decode(token, _secret(), algorithms=[ALGO])
        return int(data["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None